# Ticket: PAIML-POLA-API-002

## Title
[Infrastructure] Reconcile the 8 histogram metric names in `pole_ml/processors/histogram_processor.py`

## Description
Phase 11 (§8.3.1). The `HistogramDataProcessor` still computes the legacy metric set
(`horizontal_speed, vertical_speed, angular_speed, wrist_stability, hip_angle, knee_angle,
shoulder_angle, body_tilt_angle`). The PO confirmed a **REPLACE-to-8-signals** decision (§8.7 A-2):
the three joint-angle metrics are biomechanical *pose* features that belong to
`BiomechanicalDataProcessor`, not to the histogram's signal space. This ticket changes only the
`METRIC_NAMES` constant so the processor declares the authoritative 8 signals.

## What to Do (Implementation Steps)
- [ ] Step 1: In `packages/pole-train-model/src/pole_ml/processors/histogram_processor.py`, change `METRIC_NAMES` to `horizontal_speed, vertical_speed, angular_speed, torso_tilt_speed, wrist_stability, hip_height, body_tilt, smoothness`.
- [ ] Step 2: Drop `hip_angle`, `knee_angle`, `shoulder_angle` from `METRIC_NAMES`.
- [ ] Step 3: Rename `body_tilt_angle` → `body_tilt` (keep `horizontal_speed`, `vertical_speed`, `wrist_stability` unchanged).
- [ ] Step 4: Ensure `PHASES` and `RESAMPLED_POINTS_PER_PHASE` are untouched.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `METRIC_NAMES` equals the authoritative 8 (order preserved as M-01..M-08).
- [ ] The module imports/lints without errors.
- [ ] Existing processor tests that do not depend on the dropped angles still pass (any test asserting the old names is updated in PAIML-POLA-API-006, not here).
- [ ] No runtime computation is changed in this ticket (names only).

## Integration Tests to Run (Local Verification)
- [ ] N/A directly — verified via PAIML-POLA-API-006 (unit) and UC-91/94 (integration) after downstream tickets.

## Dependencies
- **Blocks**: PAIML-POLA-API-003, PAIML-POLA-API-004, PAIML-POLA-API-005, PAIML-POLA-API-006
- **Blocked By**: —

## Estimated Effort
- [S]
