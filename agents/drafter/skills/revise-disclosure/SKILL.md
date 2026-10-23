---
name: revise-disclosure
description: Revise the draft against open reviewer findings without touching the findings.
---

# Revise against findings

Repo root is `../../`.

1. Read `../../review/findings.csv`. Work only on rows with `status = open`.
2. For each finding, change `../../outputs/disclosure.md` and `../../outputs/coverage.csv` to address `required_fix`.
3. If a fix needs data that is not in `../../inputs/`, do not invent it. Change the coverage row to `data_gap` and add a sentence in the draft saying what is missing.
4. Append to `../../outputs/revision-log.md`:

```
## Round N
- F-012 E1.E1-8.30.a(ii): added market-based Scope 2 from inputs/emissions.yaml#scope2
- F-015 E1.E1-6.24.c: data_gap, no 1.5°C comparison in inputs
```

5. You cannot close findings. The reviewer decides in the next round whether each fix holds.
