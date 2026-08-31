# Ticket: PAIML-POLA-API-034

## Title
[Application] `GET /api/analysis/videos/{video_id}/pose`

## Description
Expose the pose read endpoint returning an annotated frame (skeleton overlay + correction hints)
with `issues`. On-demand or stored per D-A1; fall back to `detections[].frame_image_path` from
the histogram doc.

## What to Do (Implementation Steps)
- [ ] Implement `AnalysisService.get_pose(video_id)`.
- [ ] Implement `GET /api/analysis/videos/{video_id}/pose`.
- [ ] Fall back to `detections[].frame_image_path` when no on-demand pose frame is available.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pixi run test-api` passes; endpoint covered.

## Integration Tests to Run (Local Verification)
- [ ] UC-A3: analyzed video → `200` pose frame (or fallback path).

## Dependencies
- **Blocks**: PAIML-POLA-API-035
- **Blocked By**: PAIML-POLA-API-030

## Estimated Effort
- [M]
