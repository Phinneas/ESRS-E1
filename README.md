# ESRS E1 agent

A GitAgent maker-checker agent for CSRD climate disclosures. It covers ESRS 2 and ESRS E1 under the revised ESRS adopted on 3 July 2026.

Status: early build. The standards knowledge base is in. The agents are not built yet.

## What's here

- `knowledge/standards/`: every ESRS 2 and E1 requirement as CSV, with Application Requirements and EU-law datapoint links. See its README.
- `tools/parse_esrs.py`: rebuilds those files from the official text.

## Planned

- `agent.yaml` with drafter and reviewer roles, a conflict matrix, and consultant sign-off
- `agents/drafter/` and `agents/reviewer/`
- `config/client.yaml`, the one file a buyer edits

The reviewer is a review step, not assurance.
