# Ticket: PAIML-POLE-ANALYST-034

## Title
[Presentation] Modal manual de fases

## Description
Phase 10 (§1). When `detected=false` (confidence < 0.7 → `DESCONOCIDO`), open a manual phases modal
(pattern of the existing `PUT /api/training/clips/{video_id}/phase-frames`). The user drags/defines the
ENTRADA / EJECUCIÓN / SALIDA boundaries; re-launches classification & analysis with corrected phases.

## What to Do (Implementation Steps)
- [ ] Manual phases modal opening when `detected=false`.
- [ ] Drag/define ENTRADA / EJECUCIÓN / SALIDA boundaries on the video timeline.
- [ ] Submit via `savePhaseFrames` → re-launch `reanalyzeWithPhases` (job with progress).
- [ ] Unit tests: open, edit boundaries, submit + re-analysis trigger.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Modal opens when `detected=false`; corrected phases trigger re-analysis.
- [ ] `npx ng test --watch=false` green on new modules.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-035
- **Blocked By**: PAIML-POLE-ANALYST-033

## Estimated Effort
- [M]