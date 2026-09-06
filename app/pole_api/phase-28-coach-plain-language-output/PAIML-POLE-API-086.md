# Ticket: PAIML-POLE-API-086

## Title
[Coach] Z-score robustness (relative sigma floor)

## Description
Phase 28. `compute_metric_z_score` in `app/pole_api/src/tools/services/histogram_summary.py` uses `np.maximum(std, sigma_floor)` with `DEFAULT_ZSCORE_SIGMA_FLOOR = 1e-6` (`app/pole_api/src/core/config.py`), so a zero-std / degenerate reference cohort makes z explode (observed: Angular Speed Init 256635.387, Wrist Stability Init 138275.431, Torso Tilt Speed Init -114446.204).

Replace with a robust relative floor (e.g. `max(σ, scale-based floor tied to |mean|, small absolute floor)`) and/or a bounded band; keep env override semantics (`ZSCORE_SIGMA_FLOOR` still honored as a floor). Ensure tool payloads then carry sane values (`coach_insights`, `metric_deep_dive` worst_frames/detection_worst `round(z,3)`, `phase_worst`, `segment_insight` `z_score`).

## What to Do (Implementation Steps)
- [ ] Replace the absolute-only sigma floor in `compute_metric_z_score` with a robust relative floor (e.g. `max(σ, scale-based floor tied to |mean|, small absolute floor)`) and/or a bounded z band.
- [ ] Keep env override semantics: `ZSCORE_SIGMA_FLOOR` still honored as a floor.
- [ ] Verify downstream tool payloads carry sane values (`coach_insights`, `metric_deep_dive` worst_frames/detection_worst `round(z,3)`, `phase_worst`, `segment_insight` `z_score`).
- [ ] Add unit tests for `compute_metric_z_score` with std=0 and mean≈0 degenerate cases.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] z for degenerate cohorts stays within a bounded band (±~20).
- [ ] Degenerate-cohort unit tests added and green.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: None
- **Blocked By**: None

## Estimated Effort
- [S]
