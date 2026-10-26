# ESRS 2 and E1 datapoint tables

Source: revised ESRS adopted by the Commission on 3 July 2026, Delegated Regulation C(2026) 5010, Annex I. Taken from the copy sent to the Council: ST 11667/26 ADD 1 (9 July 2026).
https://data.consilium.europa.eu/doc/document/ST-11667-2026-ADD-1/en/pdf

Not yet the Official Journal text. Re-run `scripts/parse_esrs.py` when the OJ version is published and diff the CSVs.

## Files

| File | What it holds |
|---|---|
| `esrs-datapoints.csv` | One row per requirement. ESRS 2 paras 1 to 52, E1 paras 1 to 42. |
| `esrs-application-requirements.csv` | Every AR (ESRS 2: AR 1 to 47, E1: AR 1 to 32) with the paragraphs it applies to. ARs are mandatory under ESRS 1 para 18. |
| `esrs-eu-law-datapoints.csv` | Datapoints from ESRS 2 Appendix A that feed SFDR, Pillar 3, the Benchmark Regulation, or the EU Climate Law. |
| `esrs2-text.md`, `esrs-e1-text.md` | Cleaned full text, page numbers and footnotes removed. |

## Columns in esrs-datapoints.csv

- `id`: `E1.E1-8.30.a(iii)` = standard, DR, paragraph, item
- `is_leaf`: `no` for a parent item that only introduces sub-items. Count leaves only.
- `obligation`: `shall`, `may` (an option the standard gives, such as "may disclose"), `objective`, or `context` (scope and interaction text)
- `conditional`: `yes` when a condition governs the whole item ("If...", "where applicable", "if the undertaking..."), or for E1-10, which only applies if internal carbon pricing is used. Pattern match. The reviewer still checks every stated reason.
- `lead_in`: the paragraph's opening sentence when the requirement is a lettered item
- `application_requirements`: ARs that cite this paragraph or item
- `dr_has_eu_law_datapoints`: the DR contains at least one Appendix A datapoint

## Counts (leaf rows, shall or may)

- ESRS 2: 84, of which 31 conditional
- ESRS E1: 63, of which 19 conditional

These are requirement rows, not the Commission's datapoint count. One row can hold several datapoints (for example E1-8 30(a)(iii) asks for each significant Scope 3 category).

## Known limits

- Tables inside ARs (energy and GHG reporting templates) are kept as AR text, not split into rows.
- The `conditional` flag is a keyword match.
- Footnote markers glued to words were stripped by pattern. A few may remain.
- AR 24 (Scope 3) is labelled "for para. 30(c)" in the source, so the table maps it to 30(c). It reads as Scope 3 guidance, which is 30(a)(iii).
