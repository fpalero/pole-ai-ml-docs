# Ticket: PAIML-POLA-API-026

## Title
[Infrastructure] `POST /api/analysis/videos` upload endpoint

## Description
Implement the upload endpoint: accept a multipart `.mp4`, validate format/size, save the file to
the dedicated analysis folder, create an `analysis-db.videos` doc with `analyzed=false`, and
return `202 {job_id}` (+ upload record) or `201` video doc (finalize the shape per D-A1).

## What to Do (Implementation Steps)
- [ ] Define `AnalysisVideo` schema + upload request/response schemas.
- [ ] Implement `AnalysisService.upload_video` (save file + create doc).
- [ ] Implement `POST /api/analysis/videos` controller.
- [ ] Return `422` `{detail}` for non-`.mp4`/oversized (UC-A5).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pixi run test-api` passes; upload + validation covered by unit/integration tests.

## Integration Tests to Run (Local Verification)
- [ ] UC-A1: valid `.mp4` → `analysis-db.videos` doc `analyzed=false`.
- [ ] UC-A5: non-`.mp4` → `422`, no doc.

## Dependencies
- **Blocks**: PAIML-POLA-API-027, PAIML-POLA-API-029
- **Blocked By**: PAIML-POLA-API-025

## Estimated Effort
- [M]
