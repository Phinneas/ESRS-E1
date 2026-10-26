---
name: review-disclosure
description: Run one full review round on outputs/ and write review/findings.csv and review/findings.md.
---

# Review round

Repo root is `../../`.

1. Read `../../client.yaml`, `../../outputs/disclosure.md`, everything in `../../inputs/`, and the coverage files. Coverage is one file per DR at `../../outputs/coverage/<dr_code>.csv`. Take the DR codes from the `dr_code` column of `../../knowledge/standards/esrs-datapoints.csv`. A missing file means that whole DR is missing.
2. If `../../review/findings.csv` exists, load it. This is a later round. Note the round number from the prompt.
3. Run, in order:
   - skill `coverage-check`
   - skill `evidence-trace`
   - skill `claims-check`
4. In a later round, re-check each `open` finding against the current draft and `../../outputs/revision-log.md`. Set `resolved` only if the fix is actually in the text. Also check that each revision did not make a figure look cleaner than its inputs: a dropped label, source, or qualifier with the figure unchanged → **major**, check `evidence`.
5. Write `../../review/findings.csv`:

```
finding_id,round,requirement_id,check,severity,status,location,finding,required_fix
F-001,1,E1.E1-8.30.a(ii),coverage,blocking,open,E1-8 Gross Scope 1 2 3 GHG emissions,Market-based Scope 2 not reported,Add market-based Scope 2 from inputs or mark data_gap
```

   `check` is `coverage`, `evidence`, `claims`, `consistency`, or `data_gap`.
   Use `data_gap` when the only problem is that the client has not supplied the data and the draft says so honestly. Keep its severity (usually blocking). Use the other values when the draft itself is wrong.

6. Write `../../review/findings.md` in this order:
   1. One summary line: open findings by severity, split into draft problems and data gaps.
   2. **Draft problems**: table of open findings where `check` is not `data_gap`, blocking first.
   3. **Data the client must supply**: one compact table of open `data_gap` findings, grouped by DR, with what is missing.
   4. Resolved this round.
7. End your reply with: `Open draft problems: N blocking, N major, N minor. Open data gaps: N. Resolved this round: N.`
