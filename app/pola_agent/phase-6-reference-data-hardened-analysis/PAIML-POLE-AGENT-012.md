# Ticket: PAIML-POLE-AGENT-012

> **Status: PARTIALLY DONE (2026-08-13).** The pole-tools hardening suite runs via
> `pixi run test-hardening` (phase-detection <100 ms, HA-S4 LLM-down retry/fallback, fallback-rate
> gate). The API-side `test_hardening_api.py` (HA-H5/HA-S5 against the Postgres reference vertical)
> was **removed** with the deleted endpoints; the task now runs only the pole-tools tests.

## Title
[Tests] Hardened analysis integration tests (HA-H5, HA-S4/S5) + performance gates

## Description
Phase 6 hardening needs automated proof that the reference-driven pipeline is
correct and resilient.  This ticket consolidates the tests and performance
checks defined in the plan:

- **HA-H5** — Reference threshold discovery produces valid JSON in the DB with
  `0 < entrance < execution < 100`.
- **HA-S4** — LLM (`opencode serve`) timeout/down: retry once, then fallback
  advice (no crash, error logged).
- **HA-S5** — Missing reference data → 422 "Reference thresholds not trained"
  (no fabrication of feedback).

Performance targets to gate on:
- Phase detection < 100 ms per 150-frame video.
- Coaching feedback < 8 s (LLM round-trip).
- Fallback rate ≤ 5% of attempts (fail-safe must not be the common path).

These tests exercise the seeded DB (PAIML-POLE-AGENT-009), threshold discovery
(PAIML-POLE-AGENT-010), and automatic phase detection (PAIML-POLE-AGENT-011)
together, so this ticket runs last in the phase.

## What to Do (Implementation Steps)
- [ ] Add HA-H5 integration test: run `discover_thresholds` for a trick type,
  assert stored JSON validates (`0 < entrance < execution < 100`) and is
  retrievable via the thresholds endpoint.
- [ ] Add HA-S4 test: mock `OpenCodeLLMClient` to raise timeout on first call,
  succeed/raise on retry; assert fallback advice is returned and the error is
  logged; verify the 503 contract when both retries fail.
- [ ] Add HA-S5 test: with an unseeded DB / missing config, assert the analysis
  endpoint returns 422 "Reference thresholds not trained" instead of fabricated
  feedback.
- [ ] Add performance test(s): time `PhaseDetector` on a synthetic 150-frame
  signal (assert < 100 ms) and time a mocked LLM feedback round-trip
  (assert < 8 s budget accounting for mocked latency).
- [ ] Add a fallback-rate measurement: run the detection fallback logic across a
  corpus of representative attempts and assert it triggers in ≤ 5% of cases.
- [ ] Wire the new tests into the standard runners (`pixi run test`,
  `pixi run test-api`, and a new `pixi run test-hardening` if preferred).
- [ ] Document how to run the tests with a real local PostgreSQL seed for
  full-fidelity HA-H5.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] HA-H5, HA-S4, and HA-S5 integration tests exist and pass.
- [ ] Performance gates assert phase detection < 100 ms and feedback < 8 s.
- [ ] Fallback-rate check asserts ≤ 5%.
- [ ] All new tests are green and add no flaky network dependencies (LLM calls
  mocked/recorded).
- [ ] No regressions in the existing `pixi run test`, `pixi run test-jobs`,
  `pixi run test-chatbot`, and `pixi run test-api` suites.

## Integration Tests to Run (Local Verification)
- [ ] Run the full hardened suite locally with seeded PostgreSQL.
- [ ] Run UC-AG-01..06 regression against the hardened pipeline (automatic
  phase detection + reference-driven thresholds) — all must pass.
- [ ] Confirm `pixi run test-api` remains green.

## Dependencies
- **Blocks**: None (last ticket of Phase 6)
- **Blocked By**: PAIML-POLE-AGENT-009, PAIML-POLE-AGENT-010,
  PAIML-POLE-AGENT-011

## Estimated Effort
- [M]
