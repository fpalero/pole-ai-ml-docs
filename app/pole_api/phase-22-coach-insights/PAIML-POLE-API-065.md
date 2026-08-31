# Ticket: PAIML-POLE-API-065

## Title
[Infrastructure] Store fps on video doc at upload time

## Description
Phase 22 (§1). Probe fps via `pole_crop.ffmpeg.probe_metadata()` during
`AnalysisService.upload_video()` and store the value on the video document. This eliminates
repeated ffprobe subprocess calls downstream (phase durations, frame extraction timing).

For existing videos without `fps`, backfill lazily on first access.

## What to Do (Implementation Steps)
- [ ] In `AnalysisService.upload_video()`, after saving the file, call `probe_metadata(file_path)`
  from `pole_crop.ffmpeg` to get `fps`.
- [ ] Store `fps` field on the video document (add to video schema/model).
- [ ] Add `AnalysisService.get_fps(video_id) -> float` — returns stored fps or probes on-demand
  for legacy videos.
- [ ] Add `fps` field to `AnalysisVideoSummary` and any video response schemas.
- [ ] Unit tests: mock `probe_metadata`, verify fps stored, verify backfill on missing field.
- [ ] Integration test: upload video, verify fps on doc.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Uploaded videos have `fps` field on the document.
- [ ] `get_fps()` returns stored value without re-probing when available.
- [ ] `get_fps()` probes on-demand for legacy videos lacking `fps`.
- [ ] Unit tests pass for upload + backfill.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-066, PAIML-POLE-API-070
- **Blocked By**: None

## Estimated Effort
- [S]
