---
name: run-engagement
description: Run one draft-review cycle for an ESRS E1 disclosure and stop for consultant approval.
---

# Run engagement

You cannot list folders. Read files by name.

1. Read `client.yaml`. If `company.legal_name` or `company.reporting_period` is empty, stop and say which fields are missing.
2. Read `inputs/company.yaml` and `inputs/emissions.yaml`. If either is missing, stop.
3. Run the drafter:
   `gitagent --dir agents/drafter -p "Draft the ESRS 2 and E1 disclosure. Follow skill draft-disclosure."`
4. Read `outputs/coverage/E1-11.csv`. It is written last, so if it exists the draft is complete.
   If it is missing, run the drafter again with
   `-p "Resume the draft. Follow skill draft-disclosure and skip DRs whose coverage file is complete."`
   Try at most 2 resumes, then stop and report what is missing.
5. Run the reviewer:
   `gitagent --dir agents/reviewer -p "Review round 1. Follow skill review-disclosure."`
6. Read `review/findings.csv`. Count open findings by severity, separately for `check = data_gap` and everything else.
7. If any open finding with `check` other than `data_gap` is `blocking` or `major`, and rounds used is below `review.max_rounds`:
   - run the drafter with `-p "Revise against open findings in review/findings.csv. Follow skill revise-disclosure."`
   - run the reviewer with `-p "Review round N. Follow skill review-disclosure."`
   - repeat from step 6.

   Do not run another round only for data gaps. Rewording cannot fix missing data.
8. Stop. Report to the consultant:
   - rounds run
   - open draft problems by severity, with requirement IDs for every blocking one
   - the number of data gaps, and that the list is in `review/findings.md` under "Data the client must supply"
   - the exact files to read: `outputs/disclosure.md`, `review/findings.md`
   - that approval is a git commit of `approvals/<period>.md` from the consultant's own account

You do not set time limits. The guard sets each sub-agent run to one hour.

Prompts passed with `-p` must not contain quotes, `$`, backticks, `;`, `&`, `|`, `<`, `>`, or brackets. The guard blocks them.
