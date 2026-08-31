# Ticket: PAIML-POLA-API-003

## Title
[Application] Implement corrected spin/tilt metrics + `hip_height` + `smoothness` in `compute_metrics`

## Description
Phase 11 (§8.3.1). The PO corrected the physics for the two angular metrics (§8.7 A-2): the current
`angular_speed` (`d(_torso_angle)/dt`, inclination from vertical) must be **relabeled** to
`torso_tilt_speed` (M-04), and a **new** `angular_speed` (M-03) must be added as true spin (azimuth/yaw
about the vertical axis). Two brand-new signals, `hip_height` (M-06) and `smoothness` (M-08), must also
be implemented per the PO-confirmed formulas.

## What to Do (Implementation Steps)
- [ ] Step 1: Relabel the existing inclination derivative (`d(arccos(vec_y/|vec|))/dt` of `shoulder_mid − hip_mid`) as `torso_tilt_speed` (M-04).
- [ ] Step 2: Add `angular_speed` (M-03) = `d(azimuth)/dt` where `azimuth = atan2(vec_x, vec_z)` of the torso direction `shoulder_mid − hip_mid`, with `np.unwrap` before differentiating (true spin/azimuth).
- [ ] Step 3: Implement `hip_height` (M-06) = normalized hip-mid height (above ankle-mid baseline) ÷ torso length.
- [ ] Step 4: Implement `smoothness` (M-08) = inverse jerk `1 / (1 + mean|d³pos/dt³|)` (hip trajectory).
- [ ] Step 5: `body_tilt` reuses the existing `_body_tilt` computation; ensure `compute_metrics` returns exactly the 8 keys in `METRIC_NAMES` order.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `compute_metrics` returns the 8 signals with correct names, no old angle keys.
- [ ] `angular_speed` on synthetic rotation (known spin) matches expected azimuth rate; `np.unwrap` prevents ±π spikes.
- [ ] `hip_height` and `smoothness` match the CONFIRMED formulas.
- [ ] The module lints and the processor's downstream `resample` still works over the 8 keys.

## Integration Tests to Run (Local Verification)
- [ ] UC-91 / UC-94 (histogram analysis) — will be validated end-to-end after the tools slice tickets; unit-level validation lives in PAIML-POLA-API-006.

## Dependencies
- **Blocks**: PAIML-POLA-API-004, PAIML-POLA-API-006, PAIML-POLA-API-008
- **Blocked By**: PAIML-POLA-API-002

## Estimated Effort
- [L]
