"""Parse ESRS 2 and ESRS E1 from the pdftotext -layout output of the
revised ESRS delegated act annex (Council doc ST 11667/26 ADD 1).

Usage: python -I parse_esrs.py <ADD-1.txt> <out_dir>
Writes: esrs-datapoints.csv, esrs-application-requirements.csv,
        esrs-eu-law-datapoints.csv, esrs2-text.md, esrs-e1-text.md
"""
import csv
import os
import re
import sys

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
LINES = open(SRC, encoding="utf-8").read().replace("\f", "").split("\n")


def find(pattern, start=0):
    rx = re.compile(pattern)
    for i in range(start, len(LINES)):
        if rx.search(LINES[i]):
            return i
    raise SystemExit(f"not found: {pattern}")


# ---- section boundaries (0-based line indexes) ----
esrs2_start = find(r"^Objective\s*$", find(r"ESRS 2 – General Disclosures"))
appA_start = find(r"^Appendix A – List of datapoints", esrs2_start)
e1_head = find(r"ESRS E1 – Climate Change\s*$", appA_start)
e1_start = find(r"^Objective\s*$", e1_head)
e2_head = find(r"ESRS E2 – Pollution\s*$", e1_start)

PAGE_NUM = re.compile(r"^\s{30,}\d{1,3}\s*$")
FOOT_START = re.compile(r"^\s{0,4}\d{1,2}\s*$")
DR_HEAD = re.compile(r"^\s*Disclosure Requirement ([A-Z0-9]+-\d+) – (.+?)\s*$")
GDR_HEAD = re.compile(r"^\s*General Disclosure Requirement for (.+?) – (GDR-[A-Z])\s*$")
GDR_GEN = re.compile(r"^\s*General Disclosure Requirements \(GDR\) for (.+?)\s*$")
AR_BLOCK = re.compile(r"^\s*APPLICATION REQUIREMENTS")
PARA = re.compile(r"^\s{0,6}(\d{1,3})\.\s+(\S.*)$")
ITEM = re.compile(r"^\s{3,}\(([a-z]{1,4})\)\s+(\S.*)$")
ROMAN_DOT = re.compile(r"^\s{6,}((?:i|ii|iii|iv|v|vi|vii|viii|ix|x))\.\s+(\S.*)$")
FOOT_REF = re.compile(r"(?<!\bm)(?<!km)(?<=[a-z\)])(\d{1,2})(?=[\s:;,.]|$)")
AR_HEAD = re.compile(r"^\s{0,6}AR\s+(\d+)\.?\s+for\b(.*)$")
ROMAN = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii"}


def clean(lines):
    """Drop page numbers and footnotes. Keep everything else."""
    out, in_foot = [], False
    for ln in lines:
        if PAGE_NUM.match(ln):
            in_foot = False
            out.append("")
            continue
        if in_foot:
            continue
        if FOOT_START.match(ln) and ln.strip():
            in_foot = True
            continue
        out.append(ln.rstrip())
    return out


def is_heading(ln, prev_blank):
    s = ln.strip()
    return (prev_blank and s and len(s) < 45 and s[0].isupper()
            and not s.endswith((".", ";", ",", ":")) and not PARA.match(ln)
            and not ITEM.match(ln))


def parse(standard, lines):
    rows, ars = [], []
    dr_code, dr_title = f"{standard}-intro", "Objective and scope"
    para = None  # dict(num, lead, items=[...])
    item = None
    mode = "body"
    last_letter = None
    ar = None
    ar_col = None
    prev_blank = True

    def flush_para():
        nonlocal para, item
        if para is None:
            return
        lead = FOOT_REF.sub("", " ".join(para["lead"]).strip())
        if para["items"]:
            keys = [it["key"] for it in para["items"]]
            for it in para["items"]:
                parent_txt = ""
                if "(" in it["key"]:
                    par = next((p for p in para["items"] if p["key"] == it["key"].split("(")[0]), None)
                    parent_txt = FOOT_REF.sub("", " ".join(par["text"])) + " >> " if par else ""
                rows.append(dict(standard=standard, dr_code=para["dr"], dr_title=para["dr_title"],
                                 para=para["num"], item=it["key"], lead_in=lead,
                                 requirement=parent_txt + FOOT_REF.sub("", " ".join(it["text"]).strip())))
        else:
            rows.append(dict(standard=standard, dr_code=para["dr"], dr_title=para["dr_title"],
                             para=para["num"], item="", lead_in="", requirement=lead))
        para, item = None, None

    def flush_ar():
        nonlocal ar
        if ar is None:
            return
        left = " ".join(ar["left"])
        title = ""
        mt = re.search(r"\((?![a-z]{1,4}\))([A-Z][^)]*)\)?", left)
        if mt:
            title = mt.group(1).strip()
            left = left[: mt.start()]
        refs = re.findall(r"\d{1,3}(?:\s*\([a-z]{1,4}\))*", left)
        refs = [re.sub(r"\s+", "", r) for r in refs]
        ars.append(dict(standard=standard, dr_code=ar["dr"], ar=ar["num"],
                        para_refs=";".join(refs), ar_title=title,
                        text=FOOT_REF.sub("", " ".join(ar["text"]).strip())))
        ar = None

    for ln in lines:
        blank = not ln.strip()
        m = DR_HEAD.match(ln) or GDR_HEAD.match(ln) or GDR_GEN.match(ln)
        if m:
            flush_para(); flush_ar()
            mode = "body"
            if m.re is DR_HEAD:
                dr_code, dr_title = m.group(1), m.group(2)
            elif m.re is GDR_HEAD:
                dr_code, dr_title = m.group(2), f"General Disclosure Requirement for {m.group(1)}"
            else:
                dr_code, dr_title = "GDR", f"General Disclosure Requirements for {m.group(1)}"
            prev_blank = False
            continue
        if AR_BLOCK.match(ln):
            flush_para(); flush_ar()
            mode = "ar"
            prev_blank = True
            continue
        if mode == "ar":
            ma = AR_HEAD.match(ln)
            if ma:
                flush_ar()
                rest = ma.group(2)
                sp = re.search(r"\s{2,}(\S)", rest)
                left = rest[: sp.start()] if sp else rest
                right = rest[sp.start():].strip() if sp else ""
                ar_col = len(ln) - len(right) if right else 22
                ar = dict(num=int(ma.group(1)), dr=dr_code, left=[left.strip()], text=[right] if right else [])
            elif ar is not None and not blank:
                lead_ws = len(ln) - len(ln.lstrip())
                if lead_ws >= ar_col - 3:
                    ar["text"].append(ln.strip())
                else:
                    sp = re.search(r"\s{2,}(\S)", ln[lead_ws:])
                    if sp:
                        ar["left"].append(ln[lead_ws: lead_ws + sp.start()].strip())
                        ar["text"].append(ln[lead_ws + sp.start():].strip())
                    else:
                        ar["left"].append(ln.strip())
            prev_blank = blank
            continue
        # body
        if blank:
            prev_blank = True
            continue
        s = ln.strip()
        if s in ("Objective",):
            flush_para(); dr_code, dr_title = f"{standard}-objective", "Objective"; prev_blank = False; continue
        if s.startswith("Interaction with other ESRS"):
            flush_para(); dr_code, dr_title = f"{standard}-interaction", "Interaction with other ESRS"; prev_blank = False; continue
        mp = PARA.match(ln)
        if mp and (para is None or int(mp.group(1)) == para["num"] + 1 or not para["items"] or True):
            n = int(mp.group(1))
            if para is None or n > para["num"]:
                flush_para()
                para = dict(num=n, lead=[mp.group(2)], items=[], dr=dr_code, dr_title=dr_title)
                item, last_letter = None, None
                prev_blank = False
                continue
        mr = ROMAN_DOT.match(ln)
        if mr and para is not None and item is not None:
            parent = item["key"].split("(")[0]
            item = dict(key=f"{parent}({mr.group(1)})", text=[mr.group(2)])
            para["items"].append(item)
            prev_blank = False
            continue
        mi = ITEM.match(ln)
        if mi and para is not None:
            key = mi.group(1)
            is_letter = (len(key) == 1 and (last_letter is None or ord(key) == ord(last_letter) + 1)) or (
                key not in ROMAN)
            if is_letter:
                last_letter = key
                item = dict(key=key, text=[mi.group(2)])
                para["items"].append(item)
            else:  # roman sub-item under current letter
                parent = item["key"].split("(")[0] if item else ""
                item = dict(key=f"{parent}({key})" if parent else key, text=[mi.group(2)])
                para["items"].append(item)
            prev_blank = False
            continue
        if is_heading(ln, prev_blank):
            prev_blank = False
            continue
        if item is not None:
            item["text"].append(s)
        elif para is not None:
            para["lead"].append(s)
        prev_blank = False
    flush_para(); flush_ar()
    return rows, ars


def classify(r):
    t = f"{r['lead_in']} {r['requirement']}".lower()
    if r["dr_code"].endswith(("-objective", "-interaction")):
        return "context"  # scope and interaction text, not disclosure requirements
    if "objective of this dr" in t or "objective of this standard" in t:
        return "objective"
    if re.search(r"\bshall\b", t):
        return "shall"
    if re.search(r"\bmay (disclose|report|provide|present|use|include|choose)\b", t):
        return "may"
    return "context"


# DRs whose whole content only applies if the undertaking has the thing in question,
# even though the text has no "if". Reviewer still checks the stated reason.
IMPLICIT_CONDITIONAL = {
    ("ESRS E1", "E1-10"): "applies only if the undertaking uses internal carbon pricing",
}


def conditional(r):
    if (r["standard"], r["dr_code"]) in IMPLICIT_CONDITIONAL:
        return "yes"
    t = f"{r['lead_in']} {r['requirement']}".strip()
    # A condition on the whole item, not a qualifier deep inside it.
    pat = (r"(^|[.;:]\s*|>> )(if|where applicable|when providing|for social topics)\b"
           r"|\bif (the undertaking|it|such|one or more|applicable|any)\b")
    return "yes" if re.search(pat, t, re.I) else ""


# ---- parse both standards ----
e2_rows, e2_ars = parse("ESRS 2", clean(LINES[esrs2_start:appA_start]))
e1_rows, e1_ars = parse("ESRS E1", clean(LINES[e1_start:e2_head]))
rows, ars = e2_rows + e1_rows, e2_ars + e1_ars

# map ARs onto rows
ar_map = {}
for a in ars:
    for ref in filter(None, a["para_refs"].split(";")):
        mm = re.match(r"(\d+)(.*)", ref)
        num, sub = int(mm.group(1)), mm.group(2)
        letters = re.findall(r"\(([a-z]{1,4})\)", sub)
        ar_map.setdefault((a["standard"], num), []).append((letters, a["ar"]))

# ---- Appendix A: datapoints linked to other EU law ----
appA = clean(LINES[appA_start:e1_head])
eu_rows, cur, table = [], None, "main body"
ANY_ENTRY = re.compile(r"^\s{0,6}(ESRS (?:2 [A-Z]+-\d|2 GDR-[A-Z]|[ESG]\d-\d+))\b(.*)$")
NOISE = re.compile(r"Disclosure\s*$|Requirement and related datapoint( in ESRS)?|Disclosure Requirement and related datapoint in ESRS|Application Requirement in Amended ESRS|Requirement in Amended ESRS|^in ESRS$|^Disclosure$")
for ln in appA:
    if re.match(r"^\s*Table 2\.", ln):
        if cur: eu_rows.append(cur); cur = None
        table = "application requirements"
        continue
    me = ANY_ENTRY.match(ln)
    if me:
        if cur: eu_rows.append(cur)
        rest = me.group(2)
        lab = re.split(r"\s{2,}", rest.strip())[0] if rest.strip() and not rest.startswith("  ") else ""
        keep = me.group(1).startswith(("ESRS 2", "ESRS E1-"))
        cur = dict(code=me.group(1), keep=keep, table=table,
                   label=[lab] if lab and not lab.startswith(("Indicator", "Article", "Delegated", "Regulation")) else [], raw=[ln])
        continue
    if cur is None or not ln.strip():
        continue
    cur["raw"].append(ln)
    lead_ws = len(ln) - len(ln.lstrip())
    if lead_ws <= 6:
        frag = re.split(r"\s{2,}", ln.strip())[0]
        if not NOISE.search(frag):
            cur["label"].append(frag)
if cur: eu_rows.append(cur)
eu_rows = [e for e in eu_rows if e["keep"]]

eu_out = []
for e in eu_rows:
    raw = " ".join(x.strip() for x in e["raw"])
    std, dr = ("ESRS E1", e["code"].split()[1]) if "E1-" in e["code"] else ("ESRS 2", e["code"].split(" ", 2)[2])
    label = " ".join(e["label"]).strip()
    label = re.sub(r"\s*to public disclosures by institutions.*?Implementing Regulation \(EU\) 2021/637\.", "", label)
    label = re.sub(r"\b(Disclosure Requirement and related datapoint in ESRS|Requirement and related datapoint|Application Requirement in Amended ESRS|Requirement and|related datapoint|in ESRS)\b", "", label)
    label = re.sub(r"\s{2,}", " ", label).strip()
    eu_out.append(dict(standard=std, dr_code=dr, datapoint=label, appendix_table=e["table"],
                       sfdr="yes" if "Indicator" in raw else "",
                       pillar3="yes" if "449a" in raw else "",
                       benchmark_reg="yes" if "2020/1816" in raw or "2020/1818" in raw or "Delegated" in raw else "",
                       eu_climate_law="yes" if "2021/1119" in raw else ""))
eu_drs = {(e["standard"], e["dr_code"]) for e in eu_out}

# ---- write datapoints ----
with open(os.path.join(OUT, "esrs-datapoints.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    parents = {(r["standard"], r["para"], r["item"].split("(")[0]) for r in rows if "(" in r["item"]}
    w.writerow(["id", "standard", "dr_code", "dr_title", "para", "item", "is_leaf", "obligation", "conditional",
                "lead_in", "requirement", "application_requirements", "dr_has_eu_law_datapoints"])
    for r in rows:
        related = []
        for letters, arn in ar_map.get((r["standard"], r["para"]), []):
            top = r["item"].split("(")[0]
            if not letters or (top and top in letters):
                related.append(f"AR {arn}")
        rid = f"{r['standard'].replace('ESRS ', '')}.{r['dr_code']}.{r['para']}{('.' + r['item']) if r['item'] else ''}"
        leaf = "no" if (r["standard"], r["para"], r["item"]) in parents else "yes"
        w.writerow([rid, r["standard"], r["dr_code"], r["dr_title"], r["para"], r["item"], leaf, classify(r),
                    conditional(r), r["lead_in"], r["requirement"], "; ".join(sorted(set(related), key=lambda x: int(x[3:]))),
                    "yes" if (r["standard"], r["dr_code"]) in eu_drs else ""])

with open(os.path.join(OUT, "esrs-application-requirements.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["standard", "dr_code", "ar", "para_refs", "ar_title", "text"])
    w.writeheader(); w.writerows(ars)

with open(os.path.join(OUT, "esrs-eu-law-datapoints.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["standard", "dr_code", "datapoint", "appendix_table", "sfdr", "pillar3", "benchmark_reg", "eu_climate_law"])
    w.writeheader(); w.writerows(eu_out)

# raw text, cleaned, for the knowledge base
SRCNOTE = ("Source: Commission Delegated Regulation C(2026) 5010, Annex I, as transmitted to the Council "
           "(ST 11667/26 ADD 1, 9 July 2026). Adopted 3 July 2026. Text extracted automatically. "
           "Verify against the Official Journal version once published.\n\n")
for name, a, b in (("esrs2-text.md", esrs2_start, appA_start), ("esrs-e1-text.md", e1_start, e2_head)):
    txt = "\n".join(clean(LINES[a:b]))
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(SRCNOTE + "```text\n" + txt + "\n```\n")

print(f"ESRS 2 rows {len(e2_rows)}, ARs {len(e2_ars)}")
print(f"ESRS E1 rows {len(e1_rows)}, ARs {len(e1_ars)}")
print(f"EU-law datapoints (ESRS 2 + E1): {len(eu_out)}")
