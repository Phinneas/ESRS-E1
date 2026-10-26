# ESRS E1 agent

A GitAgent maker-checker system for CSRD climate disclosures. It covers ESRS 2 and ESRS E1 under the revised ESRS adopted on 3 July 2026 (Delegated Regulation C(2026) 5010).

One agent drafts the disclosure from client data. A second agent checks it against every requirement and cannot edit it. A human consultant approves. Git keeps the record.

The reviewer is a review step, not assurance.

## Status

| Part | State |
|---|---|
| Requirement tables from the adopted text | done |
| Root, drafter, reviewer agent definitions | done, pass `opengap validate --compliance` |
| Role guards that enforce segregation at runtime | done, 41 tests pass against the real runtime |
| Deterministic input and coverage checks | done |
| Fictional example with an answer key | done |
| First live run with a model | not yet. Needs an API key. |

## Layout

```
agent.yaml              orchestrator, roles, conflict matrix, handoffs
SOUL.md RULES.md DUTIES.md
client.yaml             the one file a consultant edits per engagement
inputs/                 client data (format: knowledge/methods/input-format.md)
outputs/                drafter writes here only
review/                 reviewer writes here only
approvals/              consultant commits sign-off here
agents/drafter/         drafter agent, 4 skills, hooks
agents/reviewer/        reviewer agent, 4 skills, hooks
knowledge/standards/    ESRS 2 and E1 requirements, ARs, EU-law datapoints
knowledge/methods/      input format, claims language
compliance/             risk assessment, regulatory map, validation schedule
scripts/                guard, guard tests, checks, standards parser
examples/               fictional engagement with planted problems
```

## How segregation is enforced

The gitagent CLI (2.2.0) does not enforce `segregation_of_duties` or the `tools:` list. It gives every agent shell, read, write, and edit. It also lets a tool run if a hook fails.

So every agent has `hooks/guard.sh`, which runs `scripts/guard/guard.mjs` before each tool call and fails closed:

| Agent | Read | Write | Shell |
|---|---|---|---|
| orchestrator | repo | nothing | only `gitagent --dir agents/(drafter\|reviewer) -p "..."` |
| drafter | repo, not `examples/` | `outputs/` | none |
| reviewer | repo, not `examples/` | `review/` | none |

`opengap validate --compliance` checks the role configuration. `scripts/test_guard.mjs` checks the guards using the runtime's own hook code, including real blocked writes and a crashed guard.

## Run an engagement

Needs Node 18+, git, Python 3 with PyYAML, and a model API key.

```bash
npm install -g @open-gitagent/gitagent@2.2.0      # the runtime ("gitagent" command)
mkdir -p ~/.gitagent && echo "ANTHROPIC_API_KEY=..." >> ~/.gitagent/.env   # never in the repo

# 1. fill in client.yaml and put client data in inputs/
python -I scripts/check.py inputs .               # catch data problems before any model run

# 2. run the cycle
gitagent --dir . -p "Run the engagement. Follow skill run-engagement."

# 3. read outputs/disclosure.md and review/findings.md
python -I scripts/check.py coverage .

# 4. consultant approves from their own git account
git add approvals/FY2027.md && git commit -m "Approve FY2027 E1 disclosure" && git tag e1-FY2027
```

The spec CLI also installs a `gitagent` command. Use it as `npx @open-gitagent/opengap validate --compliance`, not globally, so it does not shadow the runtime.

## Try the example

`examples/fictional-metalworks/` is an invented company with eleven planted problems. `expected-findings.md` is the answer key.

```bash
python -I scripts/check.py inputs examples/fictional-metalworks   # finds the 9 data problems
cp examples/fictional-metalworks/client.yaml . && cp examples/fictional-metalworks/inputs/*.yaml inputs/
# then step 2 above, and compare review/findings.csv with the answer key
```

The two wording problems need the reviewer agent. The script does not judge language.

## Findings from the build

- Revised E1-8 no longer requires total GHG emissions or GHG intensity per net revenue. It also has no primary-data share for Scope 3.
- AR 24 (Scope 3) is labelled "for para. 30(c)" in the adopted text. It reads as Scope 3, which is 30(a)(iii).
- The spec CLI and the runtime use different compliance field names (`risk_tier` vs `risk_level`). This repo follows the spec.

## Data and liability

Client data goes to whichever model provider the consultant configures. For EU clients, check the provider's data terms and region before the first run. `cross_border: true` is declared in `agent.yaml` for that reason.

The output is a draft for the consultant and the assurance provider. It is not legal advice and not assurance.
