# Ticket: PAIML-POLE-API-103

## Title
[Chatbot] In-flight tool call landing when turn deadline fires (option A — bounded grace budget)

## Description
Phase 29 — see [PLAN_PHASE_29](../plan/PLAN_PHASE_29.md). Follow-up to
`PAIML-POLE-API-095` (per-turn wall-clock deadline), `PAIML-POLE-API-097`
(blank hardening), and `PAIML-POLE-API-102` (gate-3 residual bundle: TOOL-08
trace + narrative backstop).

Summary: when the per-turn wall-clock deadline (095) fires while a tool call
is in-flight, the turn aborts immediately with the apology message even
though the tool succeeds milliseconds later. This ticket adds a bounded grace
budget so the in-flight tool result can land and be delivered normally; the
existing apology remains only as a true last resort when the tool itself does
not return within grace (option A — chosen by user).

Context/evidence (live staging, 2026-09-07): the execution-phase question
("What happened during the execution phase (seconds 2-6) of my handspring
video?") routes to the `segment_insight` tool (a large ~100k-token LLM call).
The per-turn wall-clock deadline (095) fires before the tool returns, so
attempt 1 aborts with the apology ("That took longer than expected… please
try again") even though the tool succeeds milliseconds later; attempt 2
(retry) returns the full segment analysis (24 frames: 6 solid / 8 adjust /
10 off). 102 (narrative backstop) already guarantees the abort reply is
well-formed — the remaining gap is the race itself.

## What to Do (Implementation Steps)
- [ ] (1) **Grace on in-flight tool, not immediate abort.** When the turn
  deadline fires while a tool call is in-flight, do NOT abort immediately:
  extend the turn with a bounded grace budget so the in-flight tool result
  can land, then deliver it normally (narrative via the existing 102
  backstop). Abort with the existing apology message ONLY if the tool itself
  does not return within the grace budget.
- [ ] (2) **Define the grace budget concretely.** Propose a constant, e.g.
  `TOOL_GRACE_DEADLINE_SECONDS` alongside the existing turn-deadline
  constant (`CHATBOT_TURN_TIMEOUT`); keep the fail-safe as a true last
  resort (grace expiry → existing apology path, unchanged message).
- [ ] (3) **Keep the timeout-distinguishable behavior from 095/102.** A real
  timeout/error still yields the `status`/`error_code` signal; only the
  racy-but-successful case changes (tool result delivered instead of
  apology). Deadline-expiry vs blank-exhaustion (097) stay distinguishable.
- [ ] (4) **Tests first (wire-level, stubbed slow `segment_insight`):**
  (a) deadline fires while tool in-flight, tool returns within grace → full
  answer arrives, no apology; (b) tool does not return within grace → apology
  + error signal preserved; (c) existing 095/102/097 suites stay green.
- [ ] (5) **Scope discipline.** Touch only the deadline handler + its tests;
  no shaping/retry/blank-policy changes (096/097 untouched).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] (1) Deadline fires while a tool call is in-flight and the tool returns
  within the grace budget → the turn delivers the tool result normally
  (narrative via the 102 backstop), with no apology message.
- [ ] (2) Tool does not return within the grace budget → the turn aborts with
  the existing apology message (unchanged text) and the existing
  `status`/`error_code` signal (095/102 behavior preserved).
- [ ] (3) Grace budget is a named constant (e.g.
  `TOOL_GRACE_DEADLINE_SECONDS`) defined alongside the existing turn-deadline
  constant; the fail-safe abort remains the last resort (documented).
- [ ] (4) Real timeouts/errors remain distinguishable from the
  racy-but-successful case: `status`/`error_code` signal present on true
  timeout/error; no signal change on the grace-landed path except the
  delivered result. 095/097 distinguishability preserved.
- [ ] (5) Only the deadline handler + its tests are touched (no
  shaping/retry/blank-policy diffs); `pixi run test-api` green, coverage
  ≥ 80% on touched files.

## Out of Scope
- Answer shaping changes (096 — empty-slot joins, nested-block
  double-encode); retry-budget / blank-policy changes (097 — blank detection,
  retry budget, model fallback); `segment_insight` payload trim / cap changes
  (093(c)); video-resolution / resolver changes (094); new contracts or FE
  changes (073/075 unchanged).

## Integration Tests to Run (Local Verification)
- [ ] Wire-level tests with a stubbed slow `segment_insight`: (a) grace-landed
  path (full answer, no apology); (b) grace-expiry path (apology + error
  signal preserved).
- [ ] Regression: existing 095/102/097 suites green (`pixi run test-api` +
  `pixi run test-chatbot`, guarded `_testing` DBs); coverage ≥ 80% on touched
  files.

## Dependencies
- **Blocks**: None (backend-only; FE contract unchanged).
- **Blocked By**: None. Related: `PAIML-POLE-API-095` (per-turn deadline —
  the race source; grace extends it), `PAIML-POLE-API-097` (blank hardening —
  distinguishability preserved, untouched), `PAIML-POLE-API-102` (narrative
  backstop — delivers the grace-landed result; TOOL-08 staging evidence),
  `PAIML-POLE-API-096` (shaping — explicitly out of scope).

## Estimated Effort
- [S]
