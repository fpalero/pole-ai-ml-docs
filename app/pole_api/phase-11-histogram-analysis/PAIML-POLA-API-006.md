# Ticket: PAIML-POLA-API-006

## Title
[Tests] Unit tests for the new/renamed metrics and cohort `mean`/`std` (pole-train-model)

## Description
Phase 11 (§8.3.1 bullet 5, §8.3.5 bullet 3). Add unit tests in `packages/pole-train-model/tests/` for
the 4 new/relabeled metrics (including azimuth unwrap for spin) and for `mean`/`std` (`ddof=1`) over
multiple resampled curves. Covers the changes in PAIML-POLA-API-002/003/004/005.

## What to Do (Implementation Steps)
- [ ] Step 1: Add synthetic-landmark fixtures with known motion (e.g. pure spin about vertical, pure sagittal tilt, pure hip raise).
- [ ] Step 2: Assert `angular_speed` (spin) and `torso_tilt_speed` (inclination) against expected values, verifying `np.unwrap` on ±π.
- [ ] Step 3: Assert `hip_height` and `smoothness` against the confirmed formulas.
- [ ] Step 4: Assert `mean`/`std` over N resampled curves (300-pt, `ddof=1`) match numpy reference.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Tests pass under `pixi run test` (pole-train-model), coverage ≥80%.
- [ ] No test asserts the dropped angle metric keys.
- [ ] Regression: existing processor/CLI tests remain green.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test` (pole-train-model) — new metric + mean/std unit tests.

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLA-API-002, PAIML-POLA-API-003, PAIML-POLA-API-004, PAIML-POLA-API-005

## Estimated Effort
- [M]
