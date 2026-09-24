# Ticket: PAIML-POLE-API-147

## Title
RE-05 Brass Monkey T3 CTA: structural emission for zero-data T3 + rag_proof fix (successful-tool filter)

- **Status**: 📋 PLANNED
- **Project**: pole_api (analyst readiness — T3 shaping + rag proof)
- **Phase**: 43 staging-gate-residuals
- **Blocks**: —
- **Blocked By**: —

## Context

Staging SAMPLE-5 gate RUN_ID `20260924-163713` scored **22/25**: VA 4/5
(VA-05 timeout), RE 3/5 (RE-04 T2-citations + RE-05 missing-CTA).
RE-01/RE-03 were fixed by 144; this ticket owns the RE-05 residual.

Binding evidence, written faithfully:

- Question: "Am I ready to attempt Brass Monkey on spin?" expects `md` +
  `retrieval_hits` + CTA + ask-once 2nd turn.
- Zero-data T3 turn emits no `readiness_cta`: the T3 CTA path in
  `answer_shaping.py:1641-1731` depends on the corpus-content branch
  (`1642-1658`) — with zero corpus content the CTA is never built.
- Even when `query_*` tools fire, `rag_proof` reads false — suspect the
  successful-tool filter / error guard drops them.
- The `_coerce` path (`blocks.py:550` `_coerce_readiness_cta_block`) must
  never drop a structurally-emitted CTA.
- Artifacts: `app/pole_analyst/test-results/coach-150q/20260924-163713/`.
- RAG ref: `pixi run docs-rag-read "coach-150q SAMPLE-5 25 questions gate" --k 5`.
- ADR: `docs/decisions/ADR-006-readiness-overall-score-gate-precondition.md`.

Prior tickets cover: 134 tiers (T1/T2/T3 contract + CTA shape), 136
deterministic retrieval, 141 tier asserts, 143/144 delegated markers, 145
spec/harness.

## Scope

1. **Structural T3 CTA** — emit `readiness_cta` for zero-data T3 without
   corpus-content branch dependence (remove/route-around
   `answer_shaping.py:1642-1658` gate); CTA must be present even when no
   corpus rows exist.
2. **Coerce-path guarantee** — ensure `_coerce_readiness_cta_block`
   (`blocks.py:550`) never drops a structurally-emitted CTA.
3. **rag_proof fix** — diagnose and fix the successful-tool filter / error
   guard that reports `rag_proof` false despite `query_*` calls firing.

Constraints (hard-stops):

- No fabrication: CTA is structural/guidance (ask-once 2nd turn), never
  invented measurements or corpus rows.
- Recommendation-only (no training-plan mutation, no medical claims).
- Single source of truth for T3/CTA markers (`readiness_tiers`) — no
  duplicated strings.
- 125/134/135/136/140/141/144/146 suites green.

Out of scope: T2 citation retrieval (146 owns that); timeout/latency
handling (148 owns that); spec/harness changes (145 pattern).

## Validation Plan

1. Hermetic replay of the Brass Monkey T3 turn: answer carries `md` +
   `retrieval_hits` + CTA with zero corpus data, across repeated runs.
2. Ask-once assertion: 2nd turn carries the CTA follow-up shape.
3. `rag_proof` true when `query_*` tools succeed (filter/guard fixed +
   asserted).
4. Regression: 125/134/135/136/140/141/144/146 suites green; T1 untouched.
5. Live battery proof deferred to gate time:
   `npx playwright test coach-150q.spec.ts --workers=1 -g "COACH7-RE-05"`.

## Acceptance Criteria

- [ ] Brass Monkey Q ("Am I ready to attempt Brass Monkey on spin?")
      returns `md` + `retrieval_hits` + CTA + ask-once 2nd turn with zero
      corpus data, across repeated hermetic runs.
- [ ] `_coerce_readiness_cta_block` never drops a structurally-emitted CTA
      (asserted).
- [ ] `rag_proof` true when `query_*` tools succeed (filter/guard root cause
      documented + fixed).
- [ ] 125/134/135/136/140/141/144/146 suites green; T1 assertions untouched.
- [ ] Live battery proof deferred to gate time — recorded, not skipped silently.

## Dependencies

- **Blocked By**: — (independent of 146/148; implement sequentially only to
  avoid shared-file conflicts in `answer_shaping.py` / `blocks.py`, not a
  ticket dependency; requires a stack serving 134+ tiers to live-validate,
  but that is environment, not a ticket dependency).
- **Blocks**: —.

## Estimated Effort

- [S] (structural CTA + coerce guarantee + rag_proof filter fix + hermetic assertions)
