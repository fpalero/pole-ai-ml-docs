# Ticket: PAIML-POLE-API-107

## Title
Analyst turn fail-safes: terminal fallback status + deterministic disclaimer

## Description
User-ordered (2026-09-09) follow-up to the 150-question gate findings on the
staging-direct run. Two APPROVED items, same turn pipeline, one ticket. Both
are server-side fail-safes on the analyst path in `app/pole_api/analyst_chatbot`
— the turn must degrade honestly instead of hanging or shipping unsafe text.

**Item 1 — Fallback terminal status.** Every graph-level fallback path must emit
a terminal WS frame (`status: Completed`, flag `fallback: true`, honest degraded
text) so the FE status pill resolves in seconds. Today fallbacks never reach
terminal status and turns hang to the 360 s budget.

**Item 2 — Deterministic `SAFETY_DISCLAIMER`.** Server-side rule: injury-labeled
turns append the disclaimer when the LLM omitted it. Mirror the 002 pole_coach
backstop pattern (`packages/pole-coach/phase-2-nodes/PAIML-POLE-COACH-002.md`:
"node deterministically appends SAFETY_DISCLAIMER when the question is
injury-related and the LLM omitted any disclaimer (fail-safe, test-covered)")
on the analyst path.

## Evidence (007 ticket gate runs)
Source: `packages/pole-coach/phase-5-integration-tests-e2e/PAIML-POLE-COACH-007.md`.

- Gate run 4 — SAMPLE-5 staging-direct (2026-09-09), RED 5/25: **Mode T — 7
  turns never complete (@360 s)**; staging `pole-api` logs `status=ABANDONED`
  on every one; graph-level fallback reply "never reaches terminal status on
  the FE. Systematic backend defects, not transient." (007 lines 203–207).
  Mode R: IN-01/02/04/05 missing `SAFETY_DISCLAIMER` (007 lines 210–211).
  Recommended follow-ups (3) "fallbacks must drive terminal FE status" and (4)
  "disclaimer + retrieval + block-contract enforcement on fallback paths" were
  NOT created — this ticket creates (3) and the disclaimer half of (4) (007
  lines 216–219).
- Gate run 3 — SAMPLE-5 retry2 (2026-09-09), RED 11/25: "deterministic
  `SAFETY_DISCLAIMER` is not enforced on the analyst path — IN-03/05 carry it
  (LLM-generated), IN-01/02/04 don't" — flagged as "follow-up ticket needed,
  NOT created" (007 lines 184–188). This ticket is that follow-up.
- Staging-log signal (run 4): 14 graph-level fallback warnings behind the 7
  hangs — every one a turn the FE never resolved.

## What to Do (Implementation Steps)
- [ ] (1) **Terminal fallback frame.** Audit every graph-level fallback path on
  the analyst turn pipeline (`app/pole_api/analyst_chatbot`): each must emit a
  terminal WS frame — `status: Completed`, `fallback: true`, plus honest
  degraded text (e.g. tools-offline wording), so the FE status pill resolves
  instead of hanging. No fallback path may end in a non-terminal state.
- [ ] (2) **Deterministic disclaimer rule.** Add a server-side post-step on the
  analyst path: when the turn is injury-labeled and the final text lacks
  `SAFETY_DISCLAIMER`, append it deterministically (mirror the 002 pole_coach
  backstop; analyst-side implementation, no `pole_coach` code touched).
- [ ] (3) **Forced-failure test.** Add a test that forces the fallback path
  (e.g. LLM/tool failure injection) and asserts a terminal `Completed` frame
  with `fallback: true` arrives (well under the 360 s budget — see
  acceptance). Add an LLM-omission test: injury-labeled turn whose LLM text
  lacks the disclaimer must still ship it.
- [ ] (4) Re-run the affected test files green; no changes to `pole_coach`
  (that package must stay langchain-free — see Out of Scope).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] (1) Forced-failure test: fallback drives a terminal WS frame
  (`Completed` + `fallback: true` + honest degraded text) in **<30 s**.
- [ ] (2) Disclaimer present on **100% of injury-labeled turns**, including the
  LLM-omission case (covered by the unit test in step 3).
- [ ] (3) No turn hangs to the 360 s budget on any fallback path exercised by
  the tests.

## Out of Scope (explicitly out — separate decisions pending)
- `metric_matrix` tool-vocabulary hygiene (register/stop-hallucinating —
  007 recommendation (1)).
- PydanticOutputParser strict-JSON / coach summary JSON hardening
  (007 recommendation (2)). Note: `langchain_core` 1.6.0 is already installed;
  `pole_coach` must stay langchain-free regardless.
- Code-owned block-contract minimums on fallback rendering (nameless matrices /
  bare-md shaping — the other half of 007 recommendation (4)).
- The above are related-future, not scope: reference them, do not implement
  them here.

## Integration Tests to Run (Local Verification)
- [ ] Forced-failure fallback test (new, step 3) — terminal frame <30 s.
- [ ] LLM-omission disclaimer test (new, step 3) — 100% disclaimer coverage.
- [ ] `pixi run test-api` (full task — must stay GREEN).

## Unit-Test Requirement
- [ ] Each fail-safe ships with its own unit test: (a) every graph-level
  fallback path emits the terminal frame; (b) the disclaimer backstop fires
  exactly when the turn is injury-labeled and the LLM text omits it (and only
  then — no double-append when the LLM already included it).

## Dependencies
- **Blocks**: Nothing (re-gate of the 25 follows implementation).
- **Blocked By**: — (standalone).

## Estimated Effort
- [S]
