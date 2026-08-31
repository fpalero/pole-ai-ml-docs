# Ticket: PAIML-POLE-FE-005

## Title
[Domain/App] Pipeline DTOs + service wiring for extract / phase-frames / histograms

## Description
`pole_fe` has no client for the extraction → process (biometric + histogram) flow that `pola_api`
already exposes. Add the DTOs and service methods the later tickets consume, mirroring the backend
contracts in `docs/app/pola_api/PLAN.md` §3 Phases 9/11/12 and §8/§9. **No BE change** — these
endpoints already exist.

Endpoints consumed (all existing):
- `POST /api/training/classes/{id}/extract` → `202 {job_id}` (body `{video_ids, extraction_stride?}`).
- `PUT /api/training/clips/{video_id}/phase-frames` → `200` (body `{phase_frames: {ENTRANCE,EXECUTION,EXIT}}`).
- `POST /api/tools/histograms/analysis` → `202 {job_id}` (body `{video_ids}`).
- `GET /api/tools/histograms/{video_id}` → `200` full doc / `404`.
- `GET /api/tools/histograms/summary/{video_id}` → `200` stored summary / `404`.

## What to Do (Implementation Steps)
- [ ] Extend `VideoRecordDto` in `core/models/api.models.ts` with `extracted?: boolean`,
      `phase_frames?: Record<string, [number, number]>`, `extraction_stride?: number | null`,
      `total_frames?: number | null`, `landmarks?: unknown[]`, `histogram_processed?: boolean`
      (fields returned verbatim by `GET /api/training/classes/{id}/videos` full-doc `_serialize`;
      `histogram_processed` is written by `pola_api` Phase 14 — `PAIML-POLA-API-036`).
- [ ] Add request/response DTOs: `ExtractRequestDto {video_ids, extraction_stride?}`,
      `PhaseFramesRequestDto {phase_frames}`, `HistogramAnalysisRequestDto {video_ids}`,
      `HistogramDto {video_id, trick_label, total_frames, phases, metrics, resampled, z_mean, scores, detections, generated_at}`,
      `HistogramSummaryDto {z_mean, scores, detections, critical_*?}` (mirror
      `app/pola_api/src/tools/schemas.py` + `histogram_summary.py`).
- [ ] Add `VideoApiService` methods (or a new `HistogramApiService`): `extract(classId, videoIds)`,
      `setPhaseFrames(videoId, phaseFrames)`, `submitHistogramAnalysis(videoIds)`,
      `getHistogram(videoId)`, `getHistogramSummary(videoId)`.
- [ ] Extend `toVideoCardModel` (`tricks/converters/tricks.converter.ts`) to carry `extracted` +
      `histogram_processed` from the DTO into the card model.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `tsc --noEmit` clean; DTO/service methods compile and hit the documented paths.
- [ ] Unit tests for the converter (mapping `extracted`/`phase_frames`) and the new service methods
      (URL + method + body), mocking `ApiClientService`.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false` (vitest runner) — new spec files pass.

## Dependencies
- **Blocks**: `PAIML-POLE-FE-006`, `PAIML-POLE-FE-007`, `PAIML-POLE-FE-008`.
- **Blocked By**: `PAIML-POLA-API-036` (writes `histogram_processed` on the video doc).

## Estimated Effort
- [M]
