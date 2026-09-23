# Ticket: PAIML-POLE-API-136

## Title
Deterministic readiness retrieval for RE-04 (tool-selection nondeterminism, same class ticket 125 cured in plan/injury)

- **Status**: ✅ DONE (merged code PR #337 → squash `b614d68`; local review APPROVED; deterministic readiness retrieval via 125-mirror domain pinning + evidence backstop + no-delegate rule; team-lead fixed 2 ruff auto-fixables pre-merge (RUF100 unused-noqa, I001 import sort); CI note: `pytest pole_api (scoped)` 25-min self-hosted-runner job timeout pattern — suite proven green locally, split/raise-timeout follow-up already recorded under 135).
- **Project**: pole_api (readiness path)
- **Phase**: 42 coach-gate-25
- **Blocks**: —
- **Blocked By**: — independent of 134/135/137.

## Context

Phase-42 gate iteration 3 (final): RED 19/25. RE-04 "What prerequisites am I
missing for the Jade split?" is a tool-selection flake on the readiness path.
Precedent: ticket 125 cured the same nondeterminism class in the plan/injury
path (now 5/5 there) — apply the equivalent enforcement to the readiness path.
RE-04's answer content is T2-style per the 134 contract (prerequisites +
recommendations); this ticket covers determinism only.

USER DECISIONS (binding): no mock data (handspring + Shoulder Mount real footage
only). Prerequisite source preference per 134: catalog edges if present else RAG
retrieval — no hand-authored test-only maps.

## Scope

Apply the 125-equivalent retrieval/tool-selection enforcement to the readiness
path for RE-04 (deterministic tool choice + grounded `rag_proof`):

- Locate the 125 enforcement in the plan/injury path and mirror it on the
  readiness path (same mechanism, readiness-scoped).
- No answer-copy changes beyond what determinism requires; T2-style content
  stays owned by 134.

## Validation Plan
1. Repeated runs (≥3):
   ```bash
   npx playwright test coach-150q.spec.ts --workers=1 -g "COACH7-RE-04"
   ```
   `rag_proof` true across all runs.
2. No regression in the plan/injury 5/5 (125 area untouched).

## Acceptance Criteria
- [ ] RE-04 `rag_proof` true across ≥3 repeated runs.
- [ ] Enforcement mirrors the 125 mechanism (cite the plan/injury enforcement
      point + the readiness mirror point).
- [ ] No hand-authored test-only prerequisite maps; no fake metrics.

## Dependencies
- **Blocked By**: — (reads 125 as precedent; 134 owns T2-style content).
- **Blocks**: —.

## Estimated Effort
- [S]
