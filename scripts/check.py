"""Deterministic checks for an ESRS E1 engagement. No model needed.

  python -I scripts/check.py inputs   <engagement_dir> [--json]
  python -I scripts/check.py coverage <engagement_dir> [--json]

<engagement_dir> holds client.yaml and inputs/ (and outputs/ for coverage).
The repo root is the engagement dir for a real engagement.
Exit code 1 if any check fails.

These checks back up the reviewer agent. They do not replace it: claims,
wording, and whether text answers a requirement still need the reviewer.
"""
import csv
import glob
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REQS = os.path.join(HERE, "..", "knowledge", "standards", "esrs-datapoints.csv")
TOL = 0.005  # 0.5%


def load(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get(d, *keys):
    for k in keys:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def close(a, b):
    return b == 0 and a == 0 or (b != 0 and abs(a - b) / abs(b) <= TOL)


class Report:
    def __init__(self):
        self.items = []

    def add(self, code, ok, requirement, message, severity="major"):
        self.items.append(dict(code=code, result="pass" if ok else "fail", requirement=requirement,
                               severity=None if ok else severity, message=message))

    def info(self, code, requirement, message):
        self.items.append(dict(code=code, result="info", requirement=requirement, severity=None, message=message))

    @property
    def failed(self):
        return [i for i in self.items if i["result"] == "fail"]

    def print(self, as_json):
        if as_json:
            print(json.dumps(self.items, indent=2))
            return
        for i in self.items:
            tag = {"pass": "PASS", "fail": "FAIL", "info": "INFO"}[i["result"]]
            sev = f" [{i['severity']}]" if i["severity"] else ""
            print(f"{tag}{sev:11} {i['code']:28} {i['requirement']:26} {i['message']}")
        print(f"\n{len(self.failed)} failed, {sum(1 for i in self.items if i['result'] == 'pass')} passed")


def check_inputs(root, r):
    client = load(os.path.join(root, "client.yaml"))
    if client is None:
        r.add("client.missing", False, "-", "client.yaml not found", "blocking")
        return
    inp = os.path.join(root, "inputs")
    company = load(os.path.join(inp, "company.yaml")) or {}
    em = load(os.path.join(inp, "emissions.yaml"))
    energy = load(os.path.join(inp, "energy.yaml"))

    for key in ("legal_name", "reporting_period"):
        r.add(f"client.{key}", bool(get(client, "company", key)), "ESRS 2 BP-1", f"client.yaml company.{key} set", "blocking")

    if em is None:
        r.add("emissions.missing", False, "E1-8", "inputs/emissions.yaml not found", "blocking")
    else:
        # boundary (AR 19)
        cb, eb = get(client, "company", "boundary_approach"), em.get("boundary")
        r.add("boundary.match", cb == eb, "E1.E1-8.30.b / AR 19",
              f"emissions boundary '{eb}' matches client.yaml '{cb}'")

        s1 = get(em, "scope1", "total_tco2e")
        r.add("scope1.present", s1 is not None, "E1.E1-8.30.a(i)", "Scope 1 total reported", "blocking")
        src = get(em, "scope1", "by_source")
        if s1 is not None and isinstance(src, dict) and src:
            tot = sum(v or 0 for v in src.values())
            r.add("scope1.by_source_sum", close(tot, s1), "E1.E1-8.30.a(i) / AR 25",
                  f"Scope 1 by source {tot:,.0f} vs total {s1:,.0f}")
        ets = get(em, "scope1", "eu_ets_tco2e")
        if s1 and ets is not None:
            r.info("scope1.eu_ets_share", "E1.E1-8.30.a(i) / AR 22", f"EU ETS share {ets / s1:.1%}")

        loc, mkt = get(em, "scope2", "location_based_tco2e"), get(em, "scope2", "market_based_tco2e")
        r.add("scope2.location", loc is not None, "E1.E1-8.30.a(ii)", "location-based Scope 2 reported", "blocking")
        r.add("scope2.market", mkt is not None, "E1.E1-8.30.a(ii)", "market-based Scope 2 reported", "blocking")

        split = em.get("consolidated_group_split") or {}
        if split and s1 is not None:
            s = (split.get("scope1_consolidated") or 0) + (split.get("scope1_other") or 0)
            r.add("split.scope1", close(s, s1), "E1.E1-8.30.c", f"Scope 1 consolidated + other {s:,.0f} vs total {s1:,.0f}")
        if split and (loc is not None or mkt is not None):
            s = (split.get("scope2_consolidated") or 0) + (split.get("scope2_other") or 0)
            ok = any(v is not None and close(s, v) for v in (loc, mkt))
            r.add("split.scope2", ok, "E1.E1-8.30.c", f"Scope 2 consolidated + other {s:,.0f} vs location {loc} / market {mkt}")

        s3 = em.get("scope3") or {}
        r.add("scope3.screening", bool(str(s3.get("screening_note") or "").strip()), "E1.E1-8.30.a(iii) / AR 24(b)",
              "Scope 3 screening across 15 categories documented")
        have = {c.get("number") for c in s3.get("categories") or []}
        want = set(get(client, "emissions", "scope3_significant_categories") or [])
        missing = sorted(want - have)
        r.add("scope3.categories", not missing, "E1.E1-8.30.a(iii)",
              f"significant categories in client.yaml all reported{'' if not missing else f', missing {missing}'}", "blocking")

        r.add("biogenic.separate", em.get("biogenic_co2_tco2e") is not None, "E1.E1-8.31",
              "biogenic CO2 reported separately (or null if none)", "minor")

        cc = em.get("carbon_credits") or {}
        own = [s for s in cc.get("standards") or [] if re.search(r"own (value chain|operations)|our supplier|in-?house", s, re.I)]
        r.add("credits.own_value_chain", not own, "E1.E1-9.34.a / AR 28(b)",
              "no credits from projects in own value chain" + (f": {own}" if own else ""), "blocking")

    # targets (AR 11, AR 17)
    for i, t in enumerate(company.get("targets") or [], 1):
        if t.get("net_zero_year"):
            r.add(f"target{i}.net_zero_residual", bool(str(t.get("residual_neutralisation") or "").strip()),
                  "E1.E1-6.23 / AR 11", f"net-zero {t['net_zero_year']} target explains residual neutralisation", "blocking")
        if t.get("science_based"):
            r.add(f"target{i}.science_based_basis", bool(str(t.get("validated_by") or "").strip()),
                  "E1.E1-6.24.c / AR 17", "science-based claim names a validator or reference pathway", "blocking")

    # transition plan (para 13)
    tp = company.get("transition_plan") or {}
    if tp.get("exists") is False:
        r.add("transition_plan.adoption", bool(str(tp.get("expected_adoption") or "").strip()), "E1.E1-1.13",
              "no plan: states whether and when one is expected", "blocking")
    elif tp.get("exists") is None:
        r.add("transition_plan.stated", False, "E1.E1-1.12 / 13", "transition plan status not given", "blocking")

    # energy (paras 26, 27)
    if energy is not None:
        for k in ("fossil_total", "nuclear_total", "renewable_total"):
            r.add(f"energy.{k}", energy.get(k) is not None, "E1.E1-7.26", f"energy {k} reported", "blocking")
        if get(client, "company", "high_climate_impact_sector"):
            fb = energy.get("fossil_breakdown") or {}
            tot = sum(v or 0 for v in fb.values())
            r.add("energy.fossil_breakdown", bool(fb) and close(tot, energy.get("fossil_total") or 0), "E1.E1-7.27",
                  f"fossil breakdown {tot:,.0f} vs fossil total {energy.get('fossil_total')}")
    else:
        r.add("energy.missing", False, "E1.E1-7.26", "inputs/energy.yaml not found", "blocking")


def check_coverage(root, r):
    single = os.path.join(root, "outputs", "coverage.csv")
    folder = os.path.join(root, "outputs", "coverage")
    files = sorted(glob.glob(os.path.join(folder, "*.csv"))) or ([single] if os.path.exists(single) else [])
    if not files:
        r.add("coverage.missing", False, "-", "no coverage files in outputs/coverage/", "blocking")
        return
    reqs = {x["id"]: x for x in csv.DictReader(open(REQS, encoding="utf-8"))
            if x["is_leaf"] == "yes" and x["obligation"] in ("shall", "may")}
    rows = {}
    for f in files:
        reader = csv.reader(open(f, encoding="utf-8"))
        header = next(reader, None) or []
        for n, cells in enumerate(reader, 2):
            if not cells:
                continue
            if len(cells) != len(header):
                where = f"{os.path.relpath(f, root)} line {n}"
                r.add(f"cov.malformed.{os.path.basename(f)}.{n}", False, cells[0] if cells else "-",
                      f"{where} has {len(cells)} columns, header has {len(header)}. Quote fields that contain commas.", "major")
                cells = (cells + [""] * len(header))[:len(header)]
            rows[cells[0]] = dict(zip(header, cells))
    if files != [single]:
        have = {os.path.splitext(os.path.basename(f))[0] for f in files}
        for dr in sorted({x["dr_code"] for x in reqs.values()} - have):
            r.add(f"cov.file.{dr}", False, dr, f"outputs/coverage/{dr}.csv missing", "blocking")
    statuses = {"disclosed", "not_applicable", "omitted_not_material", "data_gap"}
    for rid, req in reqs.items():
        row = rows.get(rid)
        if row is None:
            r.add(f"cov.{rid}", False, rid, "no coverage row", "blocking" if req["obligation"] == "shall" else "minor")
            continue
        st = row.get("status", "")
        if st not in statuses:
            r.add(f"cov.{rid}", False, rid, f"unknown status '{st}'", "major")
        elif st == "disclosed" and not row.get("section"):
            r.add(f"cov.{rid}", False, rid, "disclosed but no section named", "major")
        elif st == "not_applicable" and req["conditional"] != "yes" and req["obligation"] == "shall":
            r.add(f"cov.{rid}", False, rid, "not_applicable on a requirement with no condition", "blocking")
        elif st == "not_applicable" and not row.get("note"):
            r.add(f"cov.{rid}", False, rid, "not_applicable with no reason", "major")
        elif st == "data_gap":
            r.add(f"cov.{rid}", False, rid, "data gap: " + (row.get("note") or "no note"), "blocking")
    for rid in rows.keys() - reqs.keys():
        r.info(f"cov.extra.{rid}", rid, "row not in requirement list (check the ID)")
    done = sum(1 for k in reqs if rows.get(k, {}).get("status") in ("disclosed", "not_applicable", "omitted_not_material"))
    r.info("cov.summary", "-", f"{done} of {len(reqs)} requirements answered or justified")


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("inputs", "coverage"):
        print(__doc__)
        sys.exit(2)
    r = Report()
    (check_inputs if sys.argv[1] == "inputs" else check_coverage)(os.path.abspath(sys.argv[2]), r)
    r.print("--json" in sys.argv)
    sys.exit(1 if r.failed else 0)


if __name__ == "__main__":
    main()
