# Ticket: PAIML-POLE-API-059

## Title
[Domain + Application] Multi-frame pose schema + service + controller (`GET .../pose/frames`)

## Description
Phase 20 (§2). Create the Pydantic models, service method, and HTTP endpoint for the multi-frame
pose gallery. The Stitch FE Pose Gallery component consumes this endpoint to show multiple
annotated pose frames with skeleton overlays.

## What to Do (Implementation Steps)
- [ ] Add `PoseFrameItem` Pydantic model to `analysis/schemas.py`: `frame_number`, `frame_image_path`,
  `phase`, `metric`, `z_score`, `issues` (list of `PoseIssue`).
- [ ] Add `PoseFrameGallery` Pydantic model: `frames` (list of `PoseFrameItem`), `total_frames`.
- [ ] Add `AnalysisService.get_pose_frames(video_id)` → reads `video_histograms` doc, extracts
  `detections[]` with valid `frame_image_path`, sorts by `|z_score|` desc, wraps in
  `PoseFrameGallery`.
- [ ] Add route `GET /api/analysis/videos/{video_id}/pose/frames` in `analysis/controllers/videos.py`.
- [ ] Return `404` when no histogram exists for the video.
- [ ] Unit tests for service + controller (mock repository).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `PoseFrameItem` and `PoseFrameGallery` models exist with all fields.
- [ ] `GET .../pose/frames` returns gallery sorted by `|z_score|` desc.
- [ ] `404` when video has no histogram.
- [ ] Detections without valid `frame_image_path` are filtered out.
- [ ] Unit tests pass.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-060
- **Blocked By**: None (Phase 13 analysis slice is done)

## Estimated Effort
- [M]
