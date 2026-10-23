---
name: evidence-trace
description: Trace every figure in the draft to an input file and check the arithmetic.
---

# Evidence trace

Repo root is `../../`.

1. List every number in `../../outputs/disclosure.md` that is not a paragraph reference or a year label.
2. For each, find its `[src: ...]` tag. No tag → **blocking**.
3. Open the source file and key. The value must match, with the same unit and period. Mismatch → **blocking**.
4. A figure derived from others (a share, a sum, a split) must state how it was derived. Recompute it. Off by more than 0.5% → **major**.
5. Repeat the drafter's consistency checks independently:
   - Scope 1 by source = Scope 1 total
   - 30(c) consolidated + other = Scope 1 and Scope 2 totals
   - EU ETS share = ETS tCO2e ÷ Scope 1 tCO2e (AR 22)
   - emissions boundary = `client.yaml` boundary approach (AR 19)
   - nothing subtracts removals or credits from gross emissions (AR 20(d))
6. In `emissions.mode: calculated`, recompute every line of the working table from `inputs/activity.csv`. Any factor without a source → **blocking**.
7. Figures that agree in one section and disagree in another → **major**, check `consistency`.
