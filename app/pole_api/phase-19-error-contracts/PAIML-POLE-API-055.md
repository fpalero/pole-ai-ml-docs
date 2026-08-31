# Ticket: PAIML-POLE-API-055

## Title
[Infrastructure] Quality gates: SLA < 1 min, one-analysis-at-a-time, nota `test-hardening`

## Description
Phase 19 (§3). Close the feature quality gates:
- SLA of analysis **< 1 min** (worker pool, landmark batching).
- **One analysis at a time** (lock per video/queue).
- Tests: fake landmarks + seed of `skeleton_trick_histograms` + LSTM stub; coverage ≥ 80%;
  test DBs `pole_api_testing` / `skeleton_data_testing` / `analysis_db_testing`.
- Reintroduce the automatic-detection note in `pixi.toml` `test-hardening` (was removed).

## What to Do (Implementation Steps)
- [ ] Add worker pool / landmark batching to meet SLA < 1 min; benchmark in CI.
- [ ] Enforce one-analysis-at-a-time lock per video/queue.
- [ ] Add `pixi.toml` `test-hardening` note documenting automatic phase detection (reintroduce).
- [ ] Coverage check ≥ 80% on new modules.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] SLA < 1 min measured; one-analysis-at-a-time enforced.
- [ ] Coverage ≥ 80%; `pixi run test-api` + `pixi run test-hardening` green (guarded `_testing` DBs).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).
- [ ] `pixi run test-hardening`.

## Dependencies
- **Blocks**: None
- **Blocked By**: PAIML-POLE-API-053, PAIML-POLE-API-054

## Estimated Effort
- [M]