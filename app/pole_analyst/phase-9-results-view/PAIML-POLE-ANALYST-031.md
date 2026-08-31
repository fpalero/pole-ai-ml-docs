# Ticket: PAIML-POLE-ANALYST-031

## Title
[Domain/App] DTOs de summary (fases + scores + detections)

## Description
Phase 9 (§1, §2). Domain/App DTOs for the analysis results view: detected phases
(ENTRADA/EJECUCIÓN/SALIDA) with `start/end` + confidence, per-metric feedback (score 0-100 +
deviation vs cohort `z_mean`), and error frames from `detections[].frame_image_path`.

## What to Do (Implementation Steps)
- [ ] `PhaseResultDto` (phase, start, end, confidence).
- [ ] `MetricFeedbackDto` (metric, score, z_mean, textual feedback).
- [ ] `ErrorFrameDto` (frame_image_path, metric, phase).
- [ ] `AnalysisSummaryDto` composing phases + metrics + detections.
- [ ] Mapper from `GET /api/analysis/videos/{id}/summary` + `/histogram`.
- [ ] Unit tests for the mapping.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Summary DTOs map phases, scores, and detections from backend payloads.
- [ ] `npx ng test --watch=false` green on new modules.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-032
- **Blocked By**: PAIML-POLE-API-048

## Estimated Effort
- [M]