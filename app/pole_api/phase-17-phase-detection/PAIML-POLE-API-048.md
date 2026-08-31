# Ticket: PAIML-POLE-API-048

## Title
[Infrastructure] Integración `AnalyzeWorker` (etapa "Phase detection" + progress) + persistencia `phase_frames`

## Description
Phase 17 (§2, §4). Integrate phase detection into the analysis job pipeline. Job stages:
Extraction → Processing → **Phase detection** → Classification & analysis → Summary. Job progress per
stage; `failed`/`skipped` error-isolated (never marks job failed except corrupt video). Persist
`phase_frames` per video (start/end frames) consumed by `PUT /api/training/clips/{video_id}/phase-frames`
(manual override) and by the Summary.

## What to Do (Implementation Steps)
- [x] Add "Phase detection" stage to `AnalyzeWorker` between Processing and Classification.
- [x] Emit per-stage progress (`job_progress`) and stage states (pending/running/done/failed).
- [x] Persist `phase_frames` (detected or manual override) on the video document.
- [x] Error isolation: detection failure → `skipped` stage, job still `done` (unless corrupt video → `failed`).
- [x] Integration tests: fake landmarks pipeline reaches done with phase_frames persisted.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] Worker runs the 5-stage pipeline; `phase_frames` persisted and readable.
- [x] Detection failure does not fail the job (except corrupt video).
- [x] `pixi run test-api` green (guarded `_testing` DBs).

## Integration Tests to Run (Local Verification)
- [x] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-049, PAIML-POLE-API-052, PAIML-POLE-ANALYST-029
- **Blocked By**: PAIML-POLE-API-046, PAIML-POLE-API-047

## Estimated Effort
- [M]