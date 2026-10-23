---
name: claims-check
description: Test climate claims and wording in the draft, and in inputs/claims.yaml, against evidence.
---

# Claims check

Repo root is `../../`. Reference list: `../../knowledge/methods/claims-language.md`.

1. Scan `../../outputs/disclosure.md` for every term and pattern in the reference list.
2. Read `../../inputs/claims.yaml` if it exists. Test each claim the same way.
3. For each hit, apply the evidence test in the reference list. Not met → severity as listed there.
4. Flag forward-looking statements ("will", "aims to", "commits to") that do not name an approved plan, target, or body in the inputs → **major**.
5. Flag any sentence that presents the draft as compliant, assured, audited, or verified → **blocking**.
6. Record each as `check = claims`, quoting the exact phrase in `location`.
