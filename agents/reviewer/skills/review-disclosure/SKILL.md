---
name: review-disclosure
description: Run one full review round on outputs/ and write review/findings.csv and review/findings.md.
---

# Review round

Repo root is `../../`.

1. Read `../../client.yaml`, `../../outputs/disclosure.md`, `../../outputs/coverage.csv`, and everything in `../../inputs/`.
2. If `../../review/findings.csv` exists, load it. This is a later round. Note the round number from the prompt.
3. Run, in order:
   - skill `coverage-check`
   - skill `evidence-trace`
   - skill `claims-check`
4. In a later round, re-check each `open` finding against the current draft and `../../outputs/revision-log.md`. Set `resolved` only if the fix is actually in the text.
5. Write `../../review/findings.csv`:

```
finding_id,round,requirement_id,check,severity,status,location,finding,required_fix
F-001,1,E1.E1-8.30.a(ii),coverage,blocking,open,E1-8 Gross Scope 1 2 3 GHG emissions,Market-based Scope 2 not reported,Add market-based Scope 2 from inputs or mark data_gap
```

   `check` is `coverage`, `evidence`, `claims`, or `consistency`.

6. Write `../../review/findings.md`: a one-line summary of counts by severity and status, then a table of open blocking and major findings, then minor ones.
7. End your reply with: `Open: N blocking, N major, N minor. Resolved this round: N.`
