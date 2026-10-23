---
name: materiality-e1
description: Decide whether climate change is material and record the basis, before drafting E1.
---

# Climate materiality

Repo root is `../../`.

1. Read `client.yaml` field `materiality.climate_material` and `inputs/company.yaml` section `materiality`.
2. If both are empty, stop. Mark every E1 requirement `data_gap` and write one line in the draft: "The materiality assessment for climate change has not been provided."
3. If climate is **material**:
   - list the impacts, risks, and opportunities from the input, each with its time horizon
   - tag each risk physical or transition (E1-2 para 15)
   - every E1 DR is in scope. Topical sub-topics are mitigation, adaptation, and energy (E1 para 6).
4. If climate is **not material**:
   - E1 still needs a detailed explanation of that conclusion (E1 para 1, ESRS 1 para 30)
   - write it from `materiality.method` and the input findings only
   - mark E1 DRs `omitted_not_material` in coverage, except the explanation itself
5. Never decide materiality yourself. The client decides. You report the decision and its basis. If the basis is thin, say "basis not provided" and the reviewer will flag it.

Output: a short `## Materiality of climate change` section in `outputs/disclosure.md`, cited to inputs.
