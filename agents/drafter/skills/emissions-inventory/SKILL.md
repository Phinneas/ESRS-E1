---
name: emissions-inventory
description: Build the E1-7 energy and E1-8 emissions tables from inputs, with sources and consistency checks.
---

# Emissions and energy inventory

Repo root is `../../`. Input format: `knowledge/methods/input-format.md`.

## Mode

Read `client.yaml` → `emissions.mode`.

- `reported`: take Scope 1, 2, 3 figures from `inputs/emissions.yaml` as given.
- `calculated`: compute each line in `inputs/activity.csv` as quantity × factor, convert to tCO2e, and show the working in a table. Use the GWP set in `emissions.yaml`. If a factor or its source is missing, mark the line `data_gap`. Never pick a factor yourself.

## E1-8 table (para 30, AR 26 layout)

| Line | Requirement |
|---|---|
| Gross Scope 1 (tCO2e) | 30(a)(i) |
| % of Scope 1 from EU ETS | 30(a)(i), formula in AR 22. Only if the client has ETS sources. |
| Gross Scope 2 location-based | 30(a)(ii) |
| Gross Scope 2 market-based | 30(a)(ii) |
| Scope 3 per significant category | 30(a)(iii) |
| Scope 3 total of significant categories | 30(a)(iii) |
| Cloud and data centres, inside category 1 | AR 24(g), if applicable |
| Scope 1 and 2 split: consolidated group vs other | 30(c) |
| Biogenic CO2, separate from Scope 1 | 31 |

Add a comparative column if `comparative` is in the input (AR 26).

## Checks to run and report in the draft

- Scope 1 by source adds up to Scope 1 total (allow ±0.5%)
- 30(c) consolidated + other = Scope 1 and Scope 2 totals
- Boundary in `emissions.yaml` equals `client.yaml` boundary approach (AR 19)
- EU ETS share = ETS tCO2e ÷ Scope 1 tCO2e
- Removals and credits are not subtracted anywhere (AR 20(d))
- Scope 3 has a screening note covering all 15 categories (AR 24(b))

If a check fails, do not fix the number. Report the mismatch in the draft under `### Data quality notes`.

## E1-7 energy (paras 26 to 28)

Fossil, nuclear, renewable consumption totals in MWh. Fossil breakdown only if `high_climate_impact_sector: true`. Production split if given.

## E1-9 removals and credits (paras 33 to 35)

Report removals per project and carbon credits cancelled, purchased not cancelled, standards, and nature-based share. Credits are never inside Scope 1, 2, or 3 and never inside a reduction target.
