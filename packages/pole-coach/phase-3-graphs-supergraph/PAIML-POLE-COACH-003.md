# PAIML-POLE-COACH-003 — Phase 3 (C): graphs + supergraph + LLM router

- **Status:** 📋 PLANNED
- **Blocks:** PAIML-POLE-COACH-004, PAIML-POLE-COACH-005
- **Blocked By:** PAIML-POLE-COACH-002 (PAIML-POLE-COACH-001 for the catalog)

## Goal
Compose the Phase-2 nodes into 7 independently importable graphs plus the supergraph
with an LLM intent router, so any endpoint can bind one dedicated graph or the full
supergraph.

## Architectural context
- **Database:** readiness graph reads `trick_catalog.json` (Phase 1) +
  `slug → trick_label` alias map; no live DB.
- **Caching/performance:** graphs are pure composition (no extra LLM calls beyond the
  nodes). Router is one small classification call.
- **Scalability/resilience:** conditional edges only; every graph compiles standalone
  (`graph.compile()` test); router fallback → `query` graph on low confidence.
- **External:** none beyond Phase-2 node dependencies.

## Scope (in)
Graphs (`src/pole_coach/graphs/`, one file each, each `compile()`-able standalone):
1. `improve_trick.py` — metrics_retriever → pole → biomechanics → coach → formatter.
2. `readiness.py` — metrics_retriever → catalog lookup (level + transitions) →
   readiness gating (**latest + best historical**: prerequisite tricks via history,
   metric gates via best-historical M-01…M-05 percentiles, joint gates via
   `biomech_features`) → coach → formatter.
3. `injury.py` — metrics_retriever (risk_flags) → biomechanics → coach → formatter.
4. `training_plan.py` — profile → retrieve (pole+calisthenics+psychology) →
   coach → formatter.
5. `video_analysis.py` — metrics_retriever → biomechanics → coach → formatter.
6. `progress.py` — metrics_retriever (trend) → coach → formatter.
7. `query.py` — router → one-or-many agents → aggregator → formatter.
8. `src/pole_coach/supergraph.py` — LLM `intent_router` → conditional edges to the
   7 graphs → `END`, plus a `build_supergraph(metrics_provider, rag_provider)` factory
   injecting the protocols.
9. Unit tests: each graph compiles standalone; router maps fixture queries to the
   right graph; readiness gating unit logic (met/unmet/regressions/progressions).

## Scope (out)
Endpoint wiring, profile schema changes, biomech feature changes (Phase 4).

## Tasks
- 3.1 The 7 graphs (compose-only, no node logic duplicated).
- 3.2 `supergraph.py` + provider-injecting factory.
- 3.3 Readiness gating: catalog-driven prerequisites/regressions/progressions +
  latest+best-historical evaluation.
- 3.4 Unit tests (compile, routing fixtures, gating).

## Acceptance
- [ ] Every graph imports + compiles without the others.
- [ ] Router fixture set (≥20 queries) routes ≥90% to the expected graph.
- [ ] Unit suite green.

## Verification
`pytest packages/pole_coach`. Then **start the integration test** per ticket DoD.

## Risks
- Router misclassification → low-confidence fallback to `query` graph; logged.
- Catalog alias gaps → readiness returns "unknown trick" guidance, never fabricates.

## Definition of Done
Unit suite green → run the integration aggregator smoke and report.
