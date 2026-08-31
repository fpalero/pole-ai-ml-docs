# Ticket: PAIML-POLE-API-066

## Title
[Infrastructure] Lazy pose frame extraction on first /pose/frames access

## Description
Phase 22 (§2). The Pose tab gallery is empty because `FrameExtractor` is never called during
analysis. Detections in `video_histograms` have no `frame_image_path`.

On first `/pose/frames` access, extract JPEGs for each detection frame using
`DetectionFrameExtractor`. Store `frame_image_path` on each detection in
`video_histograms.detections[]`. Same lazy pattern as `AnalysisPoseService.ensure()`.

## What to Do (Implementation Steps)
- [ ] Create `AnalysisPoseFrameService` (or extend `AnalysisPoseService`) with `ensure(video_id)`
  method: if any detection lacks `frame_image_path`, extract frames in batch.
- [ ] Reuse `DetectionFrameExtractor.extract()` from `tools/services/frame_extractor.py`.
- [ ] Update `video_histograms.detections[]` with `frame_image_path` for each extracted frame.
- [ ] Add guard: skip extraction if `fps` is missing (call `AnalysisService.get_fps()` first).
- [ ] Wire into `GET /api/analysis/videos/{video_id}/pose/frames` controller — call `ensure()`
  before returning frames.
- [ ] Show loading spinner on FE Pose tab during extraction.
- [ ] Unit tests: mock `DetectionFrameExtractor`, verify DB update, verify skip when already extracted.
- [ ] Integration test: upload + analyze + call `/pose/frames` → verify JPEGs exist.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] First `/pose/frames` call extracts JPEGs and stores paths on detections.
- [ ] Subsequent calls return cached frames without re-extracting.
- [ ] Pose tab gallery shows thumbnail images after extraction.
- [ ] Loading state shown during extraction.
- [ ] Unit tests pass for extraction service.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-070
- **Blocked By**: PAIML-POLE-API-065 (needs fps)

## Estimated Effort
- [M]
