# Ticket: PAIML-POLE-ANALYST-030

## Title
[Presentation] ProgressPanel (5 etapas) + trigger de análisis

## Description
Phase 8 (§1, §2). Trigger analysis with `POST /api/analysis/videos/{id}/analyze` (202 job) and show a
progress panel with the 5 stages (pending/running/done/failed). Stage states derive from job
`result_json`/progress (reuse `jobs-store`). Detection stage reports `detected=true` + candidate
phases with confidence, or `detected=false` (confidence < 0.7 → `DESCONOCIDO`). Classification reports
`trick_label` (or `null`).

## What to Do (Implementation Steps)
- [ ] `analyze(videoId)` → POST `/api/analysis/videos/{id}/analyze` (202) → poll `GET /api/analysis/jobs/{job_id}`.
- [ ] ProgressPanel component rendering the 5 stages with live state.
- [ ] Surface detection result (`detected` + phases/confidence or DESCONOCIDO) and classification (`trick_label` or null).
- [ ] Unit tests: trigger + stage state rendering.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Launching analysis shows the 5-stage progress panel; stages reflect real job state.
- [ ] `npx ng test --watch=false` green on new modules.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-032, PAIML-POLE-ANALYST-033
- **Blocked By**: PAIML-POLE-ANALYST-029, PAIML-POLE-API-048

## Estimated Effort
- [M]