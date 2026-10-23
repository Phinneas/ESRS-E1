# Rules

The repo-wide rules in `../../RULES.md` also apply.

## Paths

My working folder is `agents/drafter/`. The repo root is `../../`. I write only under `../../outputs/`. The guard blocks every other write and all shell commands.

## Must always

- Write `../../outputs/disclosure.md` and `../../outputs/coverage.csv` together. Every leaf requirement in scope appears once in the coverage table.
- Put a source reference after every figure: `[src: inputs/<file>#<key>]`.
- Report Scope 2 both location-based and market-based (E1-8 para 30(a)(ii)).
- Report Scope 3 per significant category and as a total (E1-8 para 30(a)(iii)).
- Keep the GHG boundary for targets the same as for E1-8 (E1 AR 16).
- State gross targets only. No removals, credits, or avoided emissions inside a reduction target (E1 AR 12).
- If there is no transition plan, say so and say whether and when one is expected (E1 para 13).
- In `emissions.mode: reported`, use the client's totals as given and check they add up. Do not recalculate.
- In `emissions.mode: calculated`, show activity data, factor, factor source, GWP set, and result for every line.

## Must never

- Write to `../../review/`, or change a finding's status. Only the reviewer closes findings.
- Net carbon credits or removals against gross emissions (E1 AR 20(d)).
- Put biogenic CO2 from biomass in Scope 1, 2, or 3. Report it separately (E1 para 31).
- Use the words compliant, assured, verified, carbon neutral, climate neutral, net zero achieved, or green unless the input file states it and names who verified it.
- Report a total GHG figure or a revenue intensity as an E1-8 requirement. The revised E1-8 does not require them. They may appear only as voluntary context, labelled as such.
