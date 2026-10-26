---
name: revise-disclosure
description: Revise the draft against open reviewer findings without touching the findings.
---

# Revise against findings

Repo root is `../../`.

1. Read `../../review/findings.csv`. Work only on rows with `status = open`.
2. Skip rows with `check = data_gap` unless the inputs now contain the missing data. You cannot fix a gap by rewording.
3. For each other finding, change `../../outputs/disclosure.md` and the matching `../../outputs/coverage/<DR>.csv` to address `required_fix`.
4. If a fix needs data that is not in `../../inputs/`, do not invent it. Change the coverage row to `data_gap` and add a sentence in the draft saying what is missing.
5. **Never make a figure look cleaner than its inputs.** If part of a reported total does not qualify (for example credits from the client's own value chain, E1 AR 28(b)) and the inputs do not give the split:
   - keep the total exactly as reported
   - keep every source or label the input gives for it
   - state that the total includes an amount of unknown size that does not qualify
   - mark the row `data_gap` and say which split is needed

   Do not drop a label, a standard, or a qualifier to make the text match the rule.
6. Append to `../../outputs/revision-log.md`:

```
## Round N
- F-012 E1.E1-8.30.a(ii): added market-based Scope 2 from inputs/emissions.yaml#scope2
- F-015 E1.E1-6.24.c: data_gap, no 1.5°C comparison in inputs
```

   One line per finding you changed. For skipped data gaps, write one summary line with the count.

7. You cannot close findings. The reviewer decides in the next round whether each fix holds.
