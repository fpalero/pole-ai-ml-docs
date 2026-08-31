# Ticket: PAIML-POLA-API-027

## Title
[Infrastructure] `analysis` video list/get + thumbnail/stream endpoints

## Description
Implement the video read endpoints: `GET /api/analysis/videos` (list with the `analyzed` flag,
pagination), `GET /api/analysis/videos/{video_id}` (doc), and thumbnail/stream endpoints
(`/thumbnail`, `/video`).

## What to Do (Implementation Steps)
- [ ] Implement `AnalysisService.list_videos` + `get_video`.
- [ ] Implement `GET /api/analysis/videos` + `GET /api/analysis/videos/{video_id}`.
- [ ] Implement thumbnail + video streaming endpoints (mirror the video slice).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pixi run test-api` passes; list/get/stream covered by tests.

## Integration Tests to Run (Local Verification)
- [ ] UC-A1 (list returns the uploaded video), UC-A3 (thumbnail/stream served).

## Dependencies
- **Blocks**: PAIML-POLA-API-029
- **Blocked By**: PAIML-POLA-API-025, PAIML-POLA-API-026

## Estimated Effort
- [M]
