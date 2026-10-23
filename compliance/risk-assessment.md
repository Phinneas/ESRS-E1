# Risk Assessment

## Agent: esrs-e1-orchestrator (with drafter and reviewer)
## Risk Tier: high
## Assessment Date: 2026-10-23
## Assessor: [consultant to complete]

## Risk Tier Justification

The output becomes part of a legally required CSRD sustainability statement that is subject to external assurance. Errors can mislead investors and banks that rely on SFDR and Pillar 3 datapoints, and can expose the client to greenwashing claims. A human approves every release, so the agents never publish on their own.

## Applicable Regulatory Frameworks

- Directive (EU) 2022/2464 (CSRD), as amended by Directive (EU) 2026/470 (Omnibus I)
- Delegated Regulation C(2026) 5010, revised ESRS: ESRS 1, ESRS 2, ESRS E1
- Directive (EU) 2024/825 on claims (relevant to wording, not to the statement itself)
- Regulation (EU) 2016/679 (GDPR) for any personal data in inputs

## Risk Categories

| Risk | Example | Control |
|---|---|---|
| Fabricated figure | Drafter fills a missing Scope 3 category | RULES.md forbids it. Reviewer evidence-trace blocks any figure without a source. |
| Missed requirement | Market-based Scope 2 omitted | Reviewer builds the requirement list from the standard, not from the draft. `scripts/check_coverage.py` does the same in CI. |
| Self-review | Drafter edits findings | Guard blocks drafter writes to `review/`. Conflict matrix in agent.yaml. |
| Tampered draft | Reviewer rewrites the draft to pass it | Guard blocks reviewer writes to `outputs/` and all shell use. |
| Unapproved release | Agent tags a release | Guard blocks all shell for drafter and reviewer, and limits the orchestrator to launching sub-agents. Approval is a consultant git commit. |
| Misleading claim | "carbon neutral" based on credits | Reviewer claims-check, `knowledge/methods/claims-language.md` |
| Stale standard | OJ text differs from Council text | `scripts/parse_esrs.py` rebuilds the tables. Diff in git before release. |
| Data leaving the EU | Client data sent to a US-hosted model | Consultant chooses the model provider. `cross_border: true` declared. See README. |

## Mitigation Controls

- [x] Role guards with fail-closed hooks, tested by `scripts/test_guard.mjs`
- [x] Segregation of duties declared and validated (`opengap validate --compliance`)
- [x] Requirement tables from the adopted legal text
- [ ] Consultant approval process documented for the buyer
- [ ] Model provider data terms reviewed per engagement

## Approval
- [ ] Risk team approval
- [ ] Compliance team approval
- [ ] Supervisor approval
