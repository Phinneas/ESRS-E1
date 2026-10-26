# Duties

Segregation of duties for the ESRS E1 disclosure system.

## Roles

| Role | Held by | Permissions | Can write |
|---|---|---|---|
| drafter | `agents/drafter` | create, submit | `outputs/` |
| reviewer | `agents/reviewer` | review, reject, report | `review/` |
| approver | engagement consultant (human) | approve | `approvals/` (by git commit, outside the agents) |
| (coordination) | root agent | none | nothing |

## Conflict matrix

| | drafter | reviewer | approver |
|---|---|---|---|
| drafter | | conflict | conflict |
| reviewer | conflict | | conflict |
| approver | conflict | conflict | |

No agent may hold two roles. The maker cannot review or approve its own work.

## Handoff: disclosure_release

1. Drafter writes `outputs/disclosure.md` and one coverage file per DR in `outputs/coverage/`.
2. Reviewer writes `review/findings.md` and `review/findings.csv`. It cannot change the draft.
3. Drafter revises against open findings. Steps 2 and 3 repeat up to `review.max_rounds`.
4. Consultant reads the draft and findings, then commits `approvals/<period>.md` and tags the release.

A release is valid only if the approval commit is authored by the consultant and no blocking finding is open.

## Enforcement

`segregation_of_duties` in `agent.yaml` is checked by `opengap validate --compliance`. That checks the configuration only.

At runtime the gitagent CLI gives every agent every built-in tool and ignores the `tools:` list. It also lets a tool run if a hook fails. So each agent has `hooks/guard.sh`, which calls `scripts/guard/guard.mjs` before every tool call and fails closed:

- orchestrator: read anywhere in the repo, run only `gitagent --dir agents/(drafter|reviewer) -p "..."`, no writes
- drafter: read anywhere in the repo, write only under `outputs/`, no shell
- reviewer: read anywhere in the repo, write only under `review/`, no shell
- all: no reads outside the repo, no memory, MCP, or learning tools

`node scripts/test_guard.mjs <runtime path>` checks all of this against the runtime's own hook code.

## Isolation

Each sub-agent runs as its own process with its own hooks. Separate credentials are recommended: give the drafter and reviewer different API keys so their usage and logs stay separate.
