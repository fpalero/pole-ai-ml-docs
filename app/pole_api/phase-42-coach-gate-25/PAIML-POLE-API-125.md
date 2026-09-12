# Ticket: PAIML-POLE-API-125

## Title
Prompt/tool-selection: force RAG grounding for plan + trick-less injury (TP-01/03, IN-02/03)

## Status
📋 PLANNED — second in order (after PAIML-POLE-API-124; can parallelize).
Part of the phase-42 residuals split after the post-PR-#322 staging run
(`RUN_ID sample5-e743e61-20260912-083119`, images `e743e61` = PR #322 merge,
FC1–FC6 landed; score **13/25, GATE FAIL**, bar 5/5 per flow). Judge:
`<feature-wt>/app/pole_analyst/test-results/coach-150q/sample5-e743e61-20260912-083119/coach-150q-judge.md`,
transcript `coach-150q-transcript.jsonl`. The 12 fails split into exactly 3
classes → tickets 124/125/126. Gate stays 🟡 PARTIAL until full 25/25.

## Description

4 SAMPLE-5 turns produce good textual replies but ZERO RAG tool evidence —
the assertion `rag_proof` (`tool_call_names` non-empty) fails while the copy
is fine.

### Failing gate cases
- COACH7-TP-01, COACH7-TP-03 (training_plan)
- COACH7-IN-02, COACH7-IN-03 (injury)

### Evidence
Good textual replies (blocks `md,drills,quick_replies`, cards 9/4/8/2) but
`tool_call_names: []` and `rag_proof: false` — a bare-LLM answer. The
supergraph brain answers plan/injury intents WITHOUT invoking the RAG tools
(`query_pole`, `query_biomechanics`, `query_calisthenics`,
`query_psicology`) on staging's model (openrouter `deepseek/deepseek-v4-flash`).
The model is not selecting retrieval, and nothing at graph level forces it.

### Fix (owner decision pending — both options documented; deterministic recommended)
- **(A) Prompt-hardening (fallback):** tighten the system/prompt to require ≥1
  RAG tool call per plan/injury turn.
- **(B) Deterministic graph-level enforcement (DEFAULT):** plan flow always
  runs the QUERY_DOMAINS/retrieval node; trick-less injury always runs
  biomech + retrieval coach (extend the FC5 readiness pattern from
  PAIML-POLE-API-122). Tool evidence becomes structurally guaranteed instead
  of model-dependent.

Default documented fix = **(B)** with (A) as fallback.

## Files Affected
- `packages/pole_coach/src/pole_coach/graphs/_common.py`
- `app/pole_api/src/analyst_chatbot/coach_providers.py`
- prompts config
- Branch `feature/PAIML-POLE-API-125-prompt-tool-selection`.

## Validation Plan
1. BE unit tests:
   - plan turn yields ≥1 `query_*` tool call;
   - trick-less injury yields biomech + retrieval evidence, disclaimer kept.
2. Targeted battery re-run:
   `npx playwright test coach-150q.spec.ts --workers=1 -g "COACH7-(TP-01|TP-03|IN-02|IN-03|GATE)"`
   → all 4 ids flip to pass with `rag_proof` true.
3. Full SAMPLE-5 gate **25/25** as phase acceptance (with 124/126).

## Unit-Test Requirement
- [ ] Tool-selection guarantees for plan and trick-less injury flows.
- [ ] No regression on readiness/video flows.

## Integration Tests
- [ ] Targeted battery `-g "COACH7-(TP-01|TP-03|IN-02|IN-03|GATE)"` green.
- [ ] Full SAMPLE-5 gate 25/25 (with 124/126).

## Acceptance Criteria
- [ ] TP-01, TP-03, IN-02, IN-03 pass with `rag_proof=true` + tool evidence.
- [ ] Reply quality unchanged (still has drills/cards).
- [ ] Full SAMPLE-5 **25/25** (with 124/126).

## Dependencies
- **Blocked By**: none.
- **Blocks**: none.

## Estimated Effort
- [M]