---
name: draft-disclosure
description: Write outputs/disclosure.md and the per-DR coverage files in outputs/coverage/ for ESRS 2 and E1 from client inputs.
---

# Draft the disclosure

Repo root is `../../`. Read first:
- `../../client.yaml`
- every file in `../../inputs/`
- `../../knowledge/standards/esrs-datapoints.csv` (the requirement list)
- `../../knowledge/methods/input-format.md`

## Steps

1. Run skill `materiality-e1`.
2. Run skill `emissions-inventory`.
3. Build the requirement list: rows of `esrs-datapoints.csv` where `is_leaf = yes` and `obligation` is `shall` or `may`, for `ESRS 2` and `ESRS E1`.
4. Draft `../../outputs/disclosure.md` with this outline. Each heading carries its DR code so the reviewer can find it.

```
# Sustainability statement: climate (draft)
> Draft for consultant review. Not assured.
## Basis for preparation (ESRS 2 BP-1, BP-2)
## Governance (ESRS 2 GOV-1 to GOV-4)
## Strategy and business model (ESRS 2 SBM-1 to SBM-3)
## Materiality of climate change (ESRS 2 IRO-1, IRO-2)
## Climate change (ESRS E1)
### E1-1 Transition plan
### E1-2 Climate-related risks and scenario analysis
### E1-3 Resilience
### E1-4 Policies
### E1-5 Actions and resources
### E1-6 Targets
### E1-7 Energy consumption and mix
### E1-8 Gross Scope 1, 2, 3 GHG emissions
### Data quality notes
### E1-9 GHG removals and carbon credits
### E1-10 Internal carbon pricing
### E1-11 Anticipated financial effects
```

   For E1-4, E1-5, E1-6, also meet ESRS 2 GDR-P, GDR-A, GDR-T. Those rows are in the requirement list.

5. Write coverage **one DR at a time**, as soon as you finish that DR's part of the draft. One file per `dr_code` from the requirement list:

   `../../outputs/coverage/BP-1.csv`, `BP-2.csv`, `GOV-1.csv` ... `GDR.csv`, `GDR-P.csv`, `GDR-A.csv`, `GDR-M.csv`, `GDR-T.csv`, `E1-1.csv` ... `E1-11.csv`

   Each file holds only that DR's rows. Small files are written fast and survive a time-out.

   **Resuming:** if a run was cut off, read each coverage file before writing it. A file that already has a row for every requirement of its DR is done. Skip it and its part of the draft. Only redo DRs whose file is missing or incomplete.

```
requirement_id,status,section,sources,note
E1.E1-8.30.a(ii),disclosed,E1-8 Gross Scope 1 2 3 GHG emissions,inputs/emissions.yaml#scope2,
E1.E1-10.37.b,not_applicable,E1-10 Internal carbon pricing,,No internal carbon price in use (inputs/company.yaml#internal_carbon_price is empty)
```

   Put double quotes around any field that contains a comma. Five columns on every line.

   `status` is one of:
   - `disclosed`: answered in the section named
   - `not_applicable`: a conditional requirement whose condition does not apply. Say why in `note`.
   - `omitted_not_material`: climate assessed as not material
   - `data_gap`: required but not in the inputs. The draft says what is missing.

6. Write `../../outputs/coverage/E1-11.csv` last. The orchestrator checks for it to know the draft is complete.
7. End by listing every `data_gap` row.

## Style

Plain sentences. Figures with unit and period. One idea per paragraph. No adjectives that make a claim the data does not support. No forward-looking promise unless the input states it as a commitment and names who approved it.
