---
name: coverage-check
description: Check that every in-scope ESRS 2 and E1 requirement is answered, and that the coverage table is honest.
---

# Coverage check

Repo root is `../../`.

## Build the expected list yourself

From `../../knowledge/standards/esrs-datapoints.csv`, take rows where `is_leaf = yes` and `obligation` is `shall` or `may`, for `ESRS 2` and `ESRS E1`. Do not use the drafter's list as the starting point.

## For each requirement

1. Find its row in `../../outputs/coverage/<dr_code>.csv`. Missing row → **blocking** (if `shall`) or **minor** (if `may`).
2. `disclosed`: open the named section in the draft. Check the text actually answers the requirement wording in the CSV. Not answered → **blocking**.
3. `not_applicable`: the CSV row must have `conditional = yes`, and the note must say why the condition does not hold, pointing to an input. Otherwise → **major**. A non-conditional requirement marked not_applicable → **blocking**.
4. `omitted_not_material`: allowed only if climate is assessed not material. Then check the draft has the detailed explanation (E1 para 1, ESRS 1 para 30). Missing → **blocking**.
5. `data_gap`: check the draft says what is missing. Raise one **blocking** finding per gap with `check = data_gap`, so the consultant sees it. If the draft is vague about what is missing, use `check = coverage` instead.
6. Read the `application_requirements` column. Open those ARs in `esrs-application-requirements.csv` and test the ones that state a "shall". A missed AR → **major**.

## Requirements to test closely

- E1-1 para 13: no transition plan must be stated, with whether and when one is expected
- E1-6 para 24 with AR 12: targets are gross, no removals or credits inside them
- E1-6 para 24(c) with AR 17: a statement on 1.5°C compatibility, compared to a reference value
- E1-6 AR 16: target boundary equals E1-8 boundary
- E1-6 AR 11: a net-zero target explains how residual emissions are neutralised
- E1-8 para 30(a)(ii): both location-based and market-based Scope 2
- E1-8 para 30(a)(iii) with AR 24: significant Scope 3 categories identified, all 15 screened
- E1-8 para 31: biogenic CO2 shown separately
- E1-9 AR 28(b): no credits from projects inside the client's own value chain

## EU-law datapoints

For each row in `../../knowledge/standards/esrs-eu-law-datapoints.csv`, confirm it is disclosed. Missing → **blocking**, with a note that investors and banks rely on it.
