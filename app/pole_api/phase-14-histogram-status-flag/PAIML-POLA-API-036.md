# Ticket: PAIML-POLA-API-036

## Title
[Domain] Mark `videos.histogram_processed=true` on both histogram producer paths

## Description
Phase 14 (§10.3.1, D-1/D-2 — PO confirmed 2026-08-13). The FE `pole_fe` Phase 9 needs a `HISTO`
clip state without a per-clip `GET /api/tools/histograms/{video_id}` N+1. Add an additive
`histogram_processed` boolean to the app-DB `videos` doc, set to `true` whenever a per-video
histogram is successfully produced — **both** paths that write `skeleton_histograms`:
`process_service._run_process` (training `/process`) and `histogram_service._run_analysis`
(tools `/histograms/analysis`). No schema migration; default `false`.

## What to Do (Implementation Steps)
- [ ] `app/pola_api/src/training/services/process_service.py::_run_process`: after a video's
      `hist_result` is successful (not skipped/failed), call
      `VideoRepository.update(video_id, {"histogram_processed": True})` in the same loop that calls
      `mark_processed` (line ~368). Skipped videos (missing `phase_frames`) stay unflagged.
- [ ] `app/pola_api/src/tools/services/histogram_service.py::_run_analysis`: when a video is appended
      to `processed` (histogram doc present, line ~179), also
      `VideoRepository(self._database).update(video_id, {"histogram_processed": True})`. Keep
      per-video error isolation (hard rule): a flag-write failure lands in `failed`, never cancels
      the job.
- [ ] `app/pola_api/src/core/repositories/video_repository.py::_serialize`: no change needed (full-doc
      `dict(doc)` already returns `histogram_processed` when present); confirm in tests.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] After a successful `/process`, the clip's app-DB `videos` doc has `histogram_processed=true`.
- [ ] After a successful `/histograms/analysis`, each video in `result_json.processed` has
      `histogram_processed=true`; skipped/failed videos are not flagged.
- [ ] The flag is returned verbatim by `GET /api/training/classes/{id}/videos`.

## Integration Tests to Run (Local Verification)
- [ ] UC-99 / UC-100 from `docs/app/pola_api/PLAN.md` §10.5.

## Dependencies
- **Blocks**: PAIML-POLA-API-037, PAIML-POLA-API-038
- **Blocked By**: None (endpoints and histogram processors already exist)

## Estimated Effort
- [S]
