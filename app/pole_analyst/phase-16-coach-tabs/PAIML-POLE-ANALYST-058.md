# Ticket: PAIML-POLE-ANALYST-058

## Title
[Core] Coach DTOs + AnalysisService methods (coachSummary / generatePlan / poseAnalysis)

## Description
Phase 16 Phase A (PLAN_PHASE_16.md). Add the typed frontend contract for the pole_api Phase 21
coach endpoints and the service layer to consume them. Pure mappers stay framework-free under
`features/analysis/models/` (repo convention, unit-testable in isolation).

Backend contracts (see `docs/app/pole_api/plan/PLAN_PHASE_21.md`):
- `GET /api/analysis/videos/{id}/coach-summary` → `{summary, critical_insight, focus_next_session, model, generated_at}`
- `POST /api/analysis/videos/{id}/coach-plan` body `{target_trick, athlete_notes?}` →
  `{issue, weeks[4]: {week, focus, drills[]}, bail_strategy, model, generated_at}`
- `GET /api/analysis/videos/{id}/pose-analysis` → `{biomechanical_flaw, correction, aesthetic_feedback, action_step, model, generated_at}`

Errors: 404 video not found · 409 not analyzed · 503 LLM unavailable (retryable).

## What to Do (Implementation Steps)
- [ ] DTO interfaces in `core/models/api.models.ts`: `CoachSummary`, `CoachPlanWeek`,
      `ImprovementPlanDto`, `PoseAnalysis`.
- [ ] Pure view mappers in `features/analysis/models/coach.ts` (+ spec) mapping DTOs to the tab
      view shapes.
- [ ] `AnalysisService`: `coachSummary(videoId)`, `generatePlan(videoId, targetTrick, notes?)`,
      `poseAnalysis(videoId)` via `ApiClientService`.
- [ ] Error mapping through `apiInterceptor`; ensure 503 surfaces as a typed retryable error.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Service methods return typed models; errors map to `ApiError`.
- [ ] Mapper unit specs cover empty/partial payloads.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-059
- **Blocked By**: PAIML-POLE-API-064 (backend endpoints)

## Estimated Effort
- [S]
