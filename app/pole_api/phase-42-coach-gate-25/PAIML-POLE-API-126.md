# Ticket: PAIML-POLE-API-126

## Title
Empty-answer: WS per-turn wall-clock guard (VA-02, VA-05)

## Status
📋 PLANNED — third in order (can parallelize with PAIML-POLE-API-125).
Part of the phase-42 residuals split after the post-PR-#322 staging run
(`RUN_ID sample5-e743e61-20260912-083119`, images `e743e61` = PR #322 merge,
FC1–FC6 landed; score **13/25, GATE FAIL**, bar 5/5 per flow). Judge:
`<feature-wt>/app/pole_analyst/test-results/coach-150q/sample5-e743e61-20260912-083119/coach-150q-judge.md`,
transcript `coach-150q-transcript.jsonl`. The 12 fails split into exactly 3
classes → tickets 124/125/126. Gate stays 🟡 PARTIAL until full 25/25.

## Description

2 SAMPLE-5 turns hang: the FE waits the full `TURN_BUDGET_MS=360s` for
`getByRole('status', { name: /Question answered/ })` and times out; the
transcript shows ZERO `agent_reply` frames (empty reply, no blocks, no tool
calls).

### Failing gate cases
- COACH7-VA-02 (video_analysis)
- COACH7-VA-05 (video_analysis)

### Evidence / root cause
The WS router `app/pole_api/src/analyst_chatbot/router.py:255` calls
`await service.run_turn(...)` with NO per-turn wall-clock guard. The 30s
supergraph budget (`coach_providers.py:95 SUPERGRAPH_TURN_BUDGET_S`) + 120s
ReAct budget + OpenRouter tail calls can chain past the FE
`TURN_BUDGET_MS=360s` → the turn never emits a frame → the spec times out.
This is the FC4 class from PAIML-POLE-API-122 that is still unguarded.

### Fix
Wrap `run_turn` (or the whole turn section) in `asyncio.wait_for` with a
settings-driven per-turn wall-clock:
- default ~300s — above all sub-budgets, below the FE 360s budget;
- on expiry, produce a bounded terminal frame (status `error` + error_code);
  never a hang;
- settings exposed in `config.py`.
Unit test must force the deadline (asyncio timeout) and assert the terminal
frame is emitted.

## Files Affected
- `app/pole_api/src/analyst_chatbot/router.py`
- `app/pole_api/src/analyst_chatbot/config.py`
- unit test for the guard
- Branch `feature/PAIML-POLE-API-126-ws-turn-guard`.

## Validation Plan
1. BE unit test for guard expiry (forces the asyncio deadline, asserts the
   terminal frame).
2. Targeted battery re-run:
   `npx playwright test coach-150q.spec.ts --workers=1 -g "COACH7-(VA-02|VA-05|GATE)"`
   → both ids flip to pass ("Question answered" visible within budget, frames
   present).
3. Full SAMPLE-5 gate **25/25** as phase acceptance (with 124/125).

## Unit-Test Requirement
- [ ] Guard returns a terminal frame past the deadline.
- [ ] Normal (fast) turns unaffected.

## Integration Tests
- [ ] Targeted battery `-g "COACH7-(VA-02|VA-05|GATE)"` green.
- [ ] Full SAMPLE-5 gate 25/25 (with 124/125).

## Acceptance Criteria
- [ ] VA-02 + VA-05 pass in the SAMPLE-5 gate.
- [ ] No regression on fast turns.
- [ ] Full SAMPLE-5 **25/25** (with 124/125).

## Dependencies
- **Blocked By**: none.
- **Blocks**: none.

## Estimated Effort
- [S]