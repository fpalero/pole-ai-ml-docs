# Ticket: PAIML-POLA-API-012

## Title
[Infrastructure] Frame extraction (JPEG) for detected points via `pole_crop` ffmpeg

## Description
Phase 11 (§8.3.2 bullet 6). For each detected point (`|z| > 1`), extract one JPEG under a per-video
output dir using `pole_crop`/ffmpeg, and set `detections[*].frame_image_path`. This runs inside the
`analysis` job (not at read time).

## What to Do (Implementation Steps)
- [ ] Step 1: In the analysis runnable, for each detection, extract the frame (absolute frame index) to a per-video output directory.
- [ ] Step 2: Set `detections[*].frame_image_path` to the written path.
- [ ] Step 3: If extraction fails for a frame, keep the detection entry with `index/phase/metric/z_score` and omit/leave the image path (graceful degradation).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Detected points get a JPEG with `frame_image_path` set; extraction failures do not fail the job.
- [ ] Images are written under the video's output dir (reuse `pole_crop`).
- [ ] The extraction happens only in the `analysis` job, never in GET/summary.

## Integration Tests to Run (Local Verification)
- [ ] UC-91 — detections carry `frame_image_path` after analysis.

## Dependencies
- **Blocks**: PAIML-POLA-API-013
- **Blocked By**: PAIML-POLA-API-008, PAIML-POLA-API-011

## Estimated Effort
- [M]
