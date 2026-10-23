# Rules

The repo-wide rules in `../../RULES.md` also apply.

## Paths

My working folder is `agents/reviewer/`. The repo root is `../../`. I write only under `../../review/`. The guard blocks every other write and all shell commands.

## Must always

- Write `../../review/findings.csv` and `../../review/findings.md` every round.
- Give each finding a stable ID (`F-001`). Keep IDs across rounds.
- In round 2 and later, re-check every open finding and set it `resolved` or leave it `open` with a note.
- Use only the severities below.

## Severity

| Severity | Use when |
|---|---|
| blocking | A mandatory requirement in a material DR is missing or wrong. A figure has no source. A datapoint in `esrs-eu-law-datapoints.csv` is missing. A claim in the claims list is unsupported. Removals or credits are netted against emissions or counted toward a gross target. |
| major | A conditional requirement is marked not_applicable without a reason. An Application Requirement is not followed. Two parts of the draft disagree. A check in Data quality notes failed and the draft does not explain it. |
| minor | Wording, presentation, or a missing cross-reference. |

## Must never

- Edit `../../outputs/` or suggest wording beyond a one-line `required_fix`.
- Mark a requirement met because the draft says it is. Check the text.
- Close a finding the drafter marked fixed without reading the fix.
- Rate the draft overall as compliant or assured.
