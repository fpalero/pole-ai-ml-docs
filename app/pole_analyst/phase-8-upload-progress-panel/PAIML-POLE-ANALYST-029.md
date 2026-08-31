# Ticket: PAIML-POLE-ANALYST-029

## Title
[Domain/App] DTOs de job stages + mapeo de etapas

## Description
Phase 8 (§1). App/Domain layer for the analysis progress panel: job-stage DTOs and mapping of the 5
pipeline stages (Extraction, Processing, Phase detection, Classification & analysis, Summary) derived
from the job `result_json`/progress (reuse `jobs-store`).

## What to Do (Implementation Steps)
- [ ] `AnalysisStage` enum: extraction, processing, phase_detection, classification, summary.
- [ ] `JobStageDto` (stage, state pending/running/done/failed).
- [ ] Mapper from job progress/result_json → stage states.
- [ ] Unit tests: mapping for each stage state.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Job stages mapped from backend progress/result_json.
- [ ] `npx ng test --watch=false` green on new modules.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-030
- **Blocked By**: PAIML-POLE-API-048

## Estimated Effort
- [S]