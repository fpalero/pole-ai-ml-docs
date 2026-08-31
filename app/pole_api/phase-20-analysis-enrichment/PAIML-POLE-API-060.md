# Ticket: PAIML-POLE-API-060

## Title
[Testing] Multi-frame pose integration tests + UC-B3/B4/B5 validation

## Description
Phase 20 (§3, multi-frame pose). Write integration tests against `analysis_db_testing` that seed
video + histogram docs with detections and validate the multi-frame pose endpoint end-to-end.
Covers UC-B3 (happy path), UC-B4 (no detections), UC-B5 (video not analyzed → 404).

## What to Do (Implementation Steps)
- [ ] Seed 2 videos in `analysis_db_testing`: one with 5 detections (various z-scores), one
  analyzed but with 0 detections.
- [ ] Test UC-B3: `GET .../pose/frames` → `200` with `frames` array of 5, sorted by `|z_score|` desc.
  Each frame has `frame_image_path`, `phase`, `metric`, `z_score`, `issues`.
- [ ] Test UC-B4: `GET .../pose/frames` → `200` with `frames: []`, `total_frames: 0`.
- [ ] Test UC-B5: `GET .../pose/frames` for a video with no histogram → `404` `{"detail": "histogram not found"}`.
- [ ] Test detection filtering: detections without `frame_image_path` are excluded.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] All 4 integration tests pass against `analysis_db_testing`.
- [ ] Tests are isolated (clean up seeded data after run).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: None
- **Blocked By**: PAIML-POLE-API-059

## Estimated Effort
- [S]
