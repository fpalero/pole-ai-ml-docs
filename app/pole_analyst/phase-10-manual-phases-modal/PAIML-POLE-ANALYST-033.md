# Ticket: PAIML-POLE-ANALYST-033

## Title
[Domain/App] Servicios de fases manuales + trick-name + reproceso

## Description
Phase 10 (§1-§3). App/Domain services: submit manual phase boundaries (`PUT
/api/training/clips/{video_id}/phase-frames`), re-launch classification & analysis with corrected
phases, submit the athlete-provided trick name, and handle reprocessing after re-upload.

## What to Do (Implementation Steps)
- [ ] `savePhaseFrames(videoId, phases)` → PUT `/api/training/clips/{video_id}/phase-frames`.
- [ ] `reanalyzeWithPhases(videoId)` → POST `/api/analysis/videos/{id}/analyze` (re-analysis job).
- [ ] `submitTrickName(videoId, name)` → feedback/final analysis.
- [ ] `reprocess(videoId)` (re-upload already-analyzed) — idempotent; not automatic except corrupt video.
- [ ] Unit tests for each service (mock HTTP).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Services cover manual phases, trick-name, and reprocessing flows.
- [ ] `npx ng test --watch=false` green on new modules.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-034, PAIML-POLE-ANALYST-035
- **Blocked By**: PAIML-POLE-ANALYST-030, PAIML-POLE-API-054

## Estimated Effort
- [M]