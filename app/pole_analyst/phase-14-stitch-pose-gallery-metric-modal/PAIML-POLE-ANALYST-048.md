# PAIML-POLE-ANALYST-048 — Replace PoseTab with PoseGallery

## Meta
- **Project:** pole_analyst
- **Phase:** 14 — Stitch Design: Pose Gallery + Metric Detail Modal
- **Status:** TODO
- **Blocks:** PAIML-POLE-ANALYST-051
- **Blocked By:** PAIML-POLE-ANALYST-047

## Description

Replace the current `PoseTab` content with the new `PoseGalleryComponent`. The current
PoseTab fetches a single frame via `GET /api/analysis/videos/{video_id}/pose` and renders
it with `AnnotatedFrame`. The new gallery fetches multiple frames via the new endpoint
and renders the gallery layout.

### Tasks
- [ ] Update `PoseTab` to use `PoseGalleryComponent` instead of single-frame layout.
- [ ] Wire the multi-frame endpoint (`GET /api/analysis/videos/{video_id}/pose/frames`).
- [ ] Add fallback to single-frame endpoint when multi-frame is unavailable (404).
- [ ] Update PoseTab unit tests.

### Acceptance Criteria
- [ ] PoseTab shows gallery layout when multiple detections exist.
- [ ] Fallback to single-frame view when multi-frame endpoint returns 404.
- [ ] Unit tests pass.
