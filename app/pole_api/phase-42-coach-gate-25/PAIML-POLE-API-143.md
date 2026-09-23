# Ticket: PAIML-POLE-API-143

## Title
Answer-shape alignment: 141 classifier vs actual emission + PR-02 routing (shaping/routing determinism)

- **Status**: 📋 PLANNED
- **Project**: pole_api (analyst shaping + routing; gate spec `app/pole_analyst/e2e/coach-150q.spec.ts`)
- **Phase**: 42 coach-gate-25
- **Blocks**: —
- **Blocked By**: — independent of 142 (implement sequentially only to avoid shared-file conflicts, not a ticket dependency).

## Context

Local SAMPLE-5 21/25 (run `20260923-205700` + targeted rerun; report
`docs/app/pole_api/phase-42-coach-gate-25/LOCAL_GATE_20260923_2125.md` — binding
evidence). Images from develop `66a9d83` (124–141 all live, verified in-pod).
All real data, no mocks.

Prior tickets cover: 134 tiers, 135 blank-retry (2 shared retries,
graph-finalize + VA nodes), 136 determinism, 140 md-first, 141 tier asserts.

Three sub-items, one ticket — all shaping/routing determinism.

## Scope

(a) **RE-01/RE-04 tier-marker alignment:** rich grounded answers (13 and 6
tool calls) lack 134's T2 header markers — likely ReAct-delegated paths format
without terminal shaping. Align by either emitting markers on delegated paths
or teaching the classifier (141) the delegated shapes. Bidirectional decision
left to implementation, documented in the ticket's implementation note.

(b) **PR-02 routing determinism:** the model asked clarification instead of
calling `get_progress_matrix`. Add routing determinism for progress questions
with a resolved trick (mirror 125's enforcement pattern). Do NOT break
legitimate clarification when the trick is truly ambiguous — define the
boundary (resolved-trick → must call matrix tool; ambiguous-trick →
clarification allowed).

(c) **Keep T1 assertions untouched** (141 T1 matrix-rows + `rag_proof`
unchanged; no production tier-semantics changes — 134 owns those).

Out of scope: blank-retry paths (142 owns those); md-first shaping (140 owns
that); touching VA/TP/IN assertions.

## Validation Plan

1. Hermetic shape/routing assertions: delegated-path answers carry markers (or
   classifier accepts delegated shapes — per the documented bidirectional
   decision); resolved-trick progress questions deterministically route to
   `get_progress_matrix`.
2. Negative checks: T1 assertions unchanged; truly-ambiguous trick questions
   may still clarify (boundary documented + asserted).
3. Live battery proof deferred to gate time (staging down):
   `npx playwright test coach-150q.spec.ts --workers=1 -g "COACH7-(RE-01|RE-04|PR-02)"`.

## Acceptance Criteria

- [ ] T2 markers and PR-02 routing deterministic across repeated hermetic runs.
- [ ] (a) Marker emission vs classifier teaching decision documented; chosen
      direction implemented.
- [ ] (b) Resolved-trick progress questions call `get_progress_matrix`;
      ambiguous-trick clarification boundary defined and preserved.
- [ ] (c) T1 assertions untouched.
- [ ] Live battery proof deferred to gate time (staging down) — recorded, not
      skipped silently.

## Dependencies

- **Blocked By**: — (implement sequentially with 142 only to avoid
  shared-file conflicts, not a ticket dependency; requires a stack serving
  134+ tiers to live-validate, but that is environment, not a ticket
  dependency).
- **Blocks**: —.

## Estimated Effort

- [S] (shaping/routing alignment + hermetic assertions)
