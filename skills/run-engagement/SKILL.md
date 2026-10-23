---
name: run-engagement
description: Run one draft-review cycle for an ESRS E1 disclosure and stop for consultant approval.
---

# Run engagement

1. Read `client.yaml`. If `company.legal_name` or `company.reporting_period` is empty, stop and say which fields are missing.
2. List `inputs/`. If it is empty, stop.
3. Run the drafter:
   `gitagent --dir agents/drafter -p "Draft the ESRS 2 and E1 disclosure. Follow skill draft-disclosure."`
4. Confirm `outputs/disclosure.md` and `outputs/coverage.csv` exist.
5. Run the reviewer:
   `gitagent --dir agents/reviewer -p "Review round 1. Follow skill review-disclosure."`
6. Read `review/findings.csv`. Count open findings by severity.
7. If any open finding is `blocking` or `major` and rounds used is below `review.max_rounds`:
   - run the drafter with `-p "Revise against open findings in review/findings.csv. Follow skill revise-disclosure."`
   - run the reviewer with `-p "Review round N. Follow skill review-disclosure."`
   - repeat from step 6.
8. Stop. Report to the consultant:
   - rounds run
   - open findings by severity, with requirement IDs for every blocking one
   - the exact files to read: `outputs/disclosure.md`, `review/findings.md`
   - that approval is a git commit of `approvals/<period>.md` from the consultant's own account

Prompts passed with `-p` must not contain quotes, `$`, backticks, `;`, `&`, `|`, `<`, `>`, or brackets. The guard blocks them.
