# PAIML-POLE-COACH-005 — Phase 5 (E): integration tests + analyst E2E + docs

- **Status:** 📋 PLANNED
- **Blocks:** —
- **Blocked By:** PAIML-POLE-COACH-004

## Goal
Prove the whole coach end-to-end (BE graphs + analyst chat + FE), and close the
`pole-coach` docs.

## Architectural context
- **Database:** `_testing` DBs only (`POLE_API_DB`/`SKELETON_DB`/`ANALYSIS_DB` with the
  `_testing` suffix guard; never prod). E2E fakes where applicable.
- **Caching/performance:** full turn budgets honored (supergraph inherits the
  `PoleLangGraphAgent` wall-clock/blank hardening via the shared LLM path).
- **Scalability/resilience:** phase-end QA gate pattern (tester-owned integration run
  on staging `ipsf-server`, `*_test` DBs).
- **External:** staging stack only.

## Scope (in)
1. Chat-level integration tests: one scripted scenario per graph (video analysis,
   progress, query, training plan, injury, improve trick, readiness) against the
   wired `analyst_chatbot` (mocked LLM where deterministic, live where conversational).
2. `pixi run pole-analyst-e2e` extended for: new profile fields form, supergraph chat
   replies rendering existing blocks, readiness/injury/plan answers.
3. Docs close-out: `docs/packages/pole-coach/PLAN.md` states → ✅ DONE per phase,
   `docs/diagrams/pole-coach/` (FLOW + CLASSES), RAG re-embed (`docs-rag-write`).
4. Phase-end QA gate green → handover for manual acceptance (`develop` → `main` stays
   user-owned; never opened by the agent).

## Scope (out)
New features. Production data.

## Tasks
- 5.1 Seven scripted chat scenarios (assert blocks + no-blank + no-crash).
- 5.2 Analyst E2E additions (profile form, chat blocks, readiness/injury/plan).
- 5.3 Docs close-out + RAG re-embed + manifest commit.
- 5.4 Phase-end QA gate on staging.

## Acceptance
- [ ] All 7 scenarios pass; E2E green; QA gate green.
- [ ] PLAN.md states flipped; diagrams + RAG in sync.

## Verification
`pixi run test-integration`, `pixi run pole-analyst-e2e`. Then **start the
integration test** per ticket DoD (final gate).

## Risks
- LLM nondeterminism in E2E → assert on blocks/structure, not prose.

## Definition of Done
QA gate GREEN → report to user and stop (manual acceptance + `develop` → `main`
are user-owned).
