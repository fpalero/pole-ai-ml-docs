# Ticket: PAIML-POLA-API-029

## Title
[Application] `POST /api/analysis/videos/{video_id}/analyze` endpoint

## Description
Implement the analyze trigger endpoint: submit an async analysis job for a video and return
`202 {job_id}`. The job body (extract + histogram + score + flag) is implemented in
PAIML-POLA-API-030.

## What to Do (Implementation Steps)
- [ ] Define the analyze request schema.
- [ ] Implement `AnalysisService.submit_analyze(video_id)` → queue the job.
- [ ] Implement `POST /api/analysis/videos/{video_id}/analyze` controller (202).
- [ ] Return `404` if the video does not exist.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pixi run test-api` passes; endpoint returns `202 {job_id}`.

## Integration Tests to Run (Local Verification)
- [ ] UC-A2: analyze returns `202 {job_id}` and a job is queued.

## Dependencies
- **Blocks**: PAIML-POLA-API-030
- **Blocked By**: PAIML-POLA-API-026, PAIML-POLA-API-027, PAIML-POLA-API-028

## Estimated Effort
- [M]
