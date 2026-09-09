# PAIML-POLE-COACH-002 — Phase 2 (B): state schema + agent nodes + protocols

- **Status:** 📋 PLANNED
- **Blocks:** PAIML-POLE-COACH-003, PAIML-POLE-COACH-004, PAIML-POLE-COACH-005
- **Blocked By:** PAIML-POLE-COACH-001

## Goal
Implement the shared `CoachState` + typed per-agent I/O schemas and the 7 reusable nodes
(one Python file each) plus the `MetricsProvider`/`RAGProvider` protocols, so Phase 3
graphs compose them without modification.

## Architectural context
- **Database:** none (pure in-graph state). Metrics arrive as injected state, never via
  direct Mongo imports (`pole-coach` stays framework-agnostic; `pole_api` injects).
- **Caching/performance:** nodes are sync, single LLM call each (mirrors
  `CoachService._ask`: one call + one schema-validation retry). RAG retrieval capped
  (`k=3` per domain) to bound prompt size.
- **Scalability/resilience:** every node returns structured results or a typed error;
  nodes never raise to the graph (graph-level fallback → safe reply).
- **External:** LLM via `pole_chatbot.llm` (`OllamaLLM`/`build_llm`); RAG via
  `pole_rag.query.query` (collections: pole, biomechanics, calisthenics, psychology).

## Scope (in)
1. `src/pole_coach/state.py` — `CoachState` TypedDict
   (`intent, trick_name, free_question, video_id, metrics, pole_context,
   biomech_context, coach_output, rag_hits, final_blocks`) + per-agent JSON schemas
   (validated with `jsonschema`).
2. `src/pole_coach/protocols.py` — `MetricsProvider.get(video_id) →
   {scores, percentiles, risk_flags, best_historical}` and `RAGProvider.query(domain,
   text, k)`.
3. Nodes (one file each, `src/pole_coach/nodes/`):
   - `retrieve.py` — shared parametrized retrieval (domain → passages), reused by agents.
   - `pole_agent.py` — `trick_name → {description, anatomy, conditioning}` (pole RAG).
   - `biomechanics_agent.py` — `(pole_context + metrics) | free_question →
     {biomechanical_description, metric_interpretation[]}` (biomechanics RAG).
   - `coach_agent.py` — `(pole_context + biomech_context + free_question) →
     {advice, training_plan, summary, recommendation[]}` (psychology+calisthenics RAG).
   - `metrics_retriever.py` — coordinator calling the injected `MetricsProvider`.
   - `intent_router.py` — LLM intent classifier node (graph labels).
   - `formatter.py` — coach output → FE blocks (`md`, `score_summary`, `drills`,
     `metric_matrix`, `quick_replies`, `video_segment`).
4. Unit tests per node (LLM + RAG mocked): schema validation, dual-mode biomechanics
   (metrics vs free question), error paths, block shapes.

## Node contracts (7 nodes: 4 LLM-backed + 3 deterministic)

| Node | Inputs | Outputs | Prompt? |
|---|---|---|---|
| `retrieve` | `{domain, query, k=3}` | `{domain, query, hits[]}` (text + source + image meta, mirrors `rag_tools`) | No (pure RAG call; shared callable used by agent nodes) |
| `pole_agent` | `{trick_name}` (normalized via alias map) | `{description, anatomy{muscles[], joints[], contact_points[]}, conditioning[{exercise, purpose, sets_reps}]}` | Yes — P1 |
| `biomechanics_agent` | pipeline `{pole_context, metrics{scores, percentiles, risk_flags, best_historical}}` OR standalone `{free_question}` | `{biomechanical_description, metric_interpretation[{metric, percentile, phase, meaning}]}` ([] when standalone) | Yes — P2 |
| `coach_agent` | `{pole_context, biomech_context, free_question?, profile?, goal?}` | `{advice, training_plan{weeks[]+days[]}\|null, summary, recommendation[{text, priority}]}` | Yes — P3 |
| `metrics_retriever` | `{video_id}` | `{scores, percentiles, risk_flags, best_historical}` via provider | No |
| `intent_router` | `{free_question}` | `{intent, confidence}` (7 labels; fallback `query`) | Yes — P4 |
| `formatter` | `{coach_output, biomech_context?, pole_context?, video_id?}` | `{final_blocks[]}` (md/score_summary/drills/metric_matrix/quick_replies/video_segment/image) | No (template mapping) |

Prompts (full prose written in implementation; required sections):
- **P1 (pole):** persona=elite pole technique expert; inputs=trick_name + pole passages;
  rules=grounded-only, JSON-schema output.
- **P2 (biomechanics):** persona=biomechanics; inputs=pole_context + metrics (phase-level
  interpretation, M-01…M-05 + joint angles) OR free_question; rules=grounded-only,
  JSON-schema output.
- **P3 (coach):** persona=head coach, athlete-facing plain language; inputs=pole +
  biomech + psych/calisthenics passages + profile/goal; safety disclaimer when
  injury-related; JSON-schema output.
- **P4 (router):** 7 labels + definitions + few-shot examples; JSON `{intent,
  confidence}`; low-confidence → `query`.

## Scope (out)
Graph composition, supergraph, endpoint wiring, catalog-gated readiness logic (Phase 3).

## Tasks
- 2.1 `state.py` + JSON schemas (+ validation helper).
- 2.2 `protocols.py` (provider interfaces + fake implementations for tests).
- 2.3 The 7 nodes, each in its own file, reusing `pole_chatbot.llm` and
  `pole_rag.query` (no duplicated LLM/RAG plumbing).
- 2.4 Metrics contract: only M-01…M-05 keys + known `FEATURE_NAMES` joints accepted.
- 2.5 Unit tests per node.

## Acceptance
- [ ] All nodes import independently and run standalone with fakes.
- [ ] Agent outputs validate against schemas; invalid LLM JSON triggers the single retry,
  then a typed error (never a crash).
- [ ] Unit suite green.

## Verification
`pytest packages/pole_coach`. Then **start the integration test** per ticket DoD.

## Risks
- LLM JSON drift → mitigated by schema + retry + typed errors.
- Metric vocabulary drift (M-06…M-08) → nodes reject unknown metric keys loudly.

## Definition of Done
Unit suite green → run the integration aggregator smoke and report.

## As-built deviations (implementation report)
1. No FEATURE_NAMES constant exists anywhere (verified by grep over pole-train-model, pole-tools, chatbot) — defined KNOWN_JOINTS = the 4 joint angles the extractor actually measures (left/right_elbow/knee_deg), enforced on optional joint_angles payload; UC-13/004 extends the set.
2. Intent labels not enumerated in ticket — used Phase-4 scenario names from the plan (UC-15..21): video_analysis, progress, query, training_plan, injury, improve_trick, readiness.
3. Coach safety backstop: node deterministically appends SAFETY_DISCLAIMER when the question is injury-related and the LLM omitted any disclaimer (fail-safe, test-covered).
4. Router never errors: LLM failure yields {"intent": "query", "confidence": 0.0}; low-confidence threshold 0.5.
5. formatter accepts optional rag_hits (from CoachState.rag_hits) to emit image blocks.

Implementation HEAD 5d9cb0e, worktree branch feature/PAIML-POLE-COACH-002-state-schema-nodes, unit `pixi run test-polecoach` 104 passed.
