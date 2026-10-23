# Expected findings

Answer key for the fictional Harbourline Metalworks engagement. A correct reviewer run raises at least these. `scripts/check.py inputs` catches the ones marked **script** without a model.

| # | Planted problem | Requirement | Expected severity | Caught by |
|---|---|---|---|---|
| 1 | Market-based Scope 2 missing | E1.E1-8.30.a(ii) | blocking | script, reviewer coverage |
| 2 | Scope 1 by source sums to 4,950, total says 5,200 | E1.E1-8.30.a(i), AR 25 | major | script, reviewer evidence |
| 3 | Consolidated + other Scope 1 is 5,100, total says 5,200 | E1.E1-8.30.c(i), (ii) | major | script, reviewer evidence |
| 4 | Net-zero 2040 target with no residual neutralisation plan | E1.E1-6.23, AR 11 | blocking | script, reviewer coverage |
| 5 | Target says science-based but no validator and no 1.5°C comparison | E1.E1-6.24.c, AR 17 | blocking | script, reviewer coverage, claims |
| 6 | Emissions boundary (operational control) differs from client.yaml (financial control) | E1.E1-8.30.b, AR 19 | major | script, reviewer evidence |
| 7 | No transition plan and no statement of whether or when one is expected | E1.E1-1.13 | blocking | script, reviewer coverage |
| 8 | No Scope 3 screening across the 15 categories | E1.E1-8.30.a(iii), AR 24(b) | major | script, reviewer coverage |
| 9 | Carbon credits from a project in the client's own value chain | E1.E1-9.34.a, AR 28(b) | blocking | script, reviewer coverage |
| 10 | "Carbon neutral since 2025" resting on credits | E1-9, claims-language | blocking | reviewer claims |
| 11 | "Greenest structural steel in the Nordics" with no evidence | claims-language | major | reviewer claims |

Also expected because the drafter has no data:
- E1-10 internal carbon pricing: `not_applicable` with a reason (list is empty). Not a finding if the reason is given.
- E1-11 several financial-effect datapoints: `data_gap` (blocking each) for assets at transition risk, real estate by energy class, and opportunities revenue.

Should **not** be flagged:
- EU ETS share 3,900 ÷ 5,200 = 75.0%
- Biogenic CO2 120 t reported separately
- Energy fossil breakdown (high climate impact sector) adds up: 900 + 15,800 + 4,700 = 21,400
