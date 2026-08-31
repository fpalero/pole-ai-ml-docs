# Ticket: PAIML-POLE-ANALYST-011

## Title
[Application] VideosService — upload video

## Description
Implement the upload write side: `POST /api/analysis/videos` (multipart `.mp4`) with progress
reporting, and poll the resulting upload job via `GET /api/analysis/jobs/{job_id}` for
verification. After success, refresh the library.

## What to Do (Implementation Steps)
- [ ] Implement `VideosService.upload(file)` → multipart POST with progress events.
- [ ] Track the returned job and poll `GET /api/analysis/jobs/{job_id}` until verified.
- [ ] Emit success/failure to the library store.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] Upload progress + job polling are unit-tested with a mocked client.

## Integration Tests to Run (Local Verification)
- [ ] UC-01: `.mp4` upload shows progress and then appears in the list; UC-05: rejected file
      surfaces an error.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-012, PAIML-POLE-ANALYST-021
- **Blocked By**: PAIML-POLE-ANALYST-002

## Estimated Effort
- [M]
