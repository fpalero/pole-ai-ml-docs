# Fase 16 — Coach tabs (contenido LLM estructurado en Summary / Plan / Pose) — ✅ DONE

> Plan maestro: [PLAN.md](../PLAN.md) · Backend requerido: `pole_api` Phase 21 (coach endpoints,
> tickets PAIML-POLE-API-062..064)

## Contexto

The three athlete-facing tabs currently render rule-based content, except Plan which parses the
last chat `agent_reply` free-text (`models/plan.ts`). The backend Phase 21 adds deterministic
one-shot coach endpoints that persist structured LLM coaching content on the video doc:

1. **Performance Summary** — `{summary, critical_insight, focus_next_session}`
2. **Improvement Plan** — `{issue, weeks[4]: {week, focus, drills[]}, bail_strategy}`
3. **Static Pose Analysis** — `{biomechanical_flaw, correction, aesthetic_feedback, action_step}`

This phase consumes them in `pole_analyst`. Structured JSON replaces markdown parsing as the
primary contract; the existing `plan.ts` parser stays as fallback for legacy chat replies.

## Alcance

### 1. Core models + service methods

New DTOs in `core/models/api.models.ts`: `CoachSummary`, `CoachPlanWeek`, `ImprovementPlanDto`,
`PoseAnalysis`, each mirroring the backend JSON contracts plus the envelope fields
(`model`, `generated_at`). New `AnalysisService` methods:

- `coachSummary(videoId)` → GET `/api/analysis/videos/{id}/coach-summary`
- `generatePlan(videoId, targetTrick, notes?)` → POST `.../coach-plan`
- `poseAnalysis(videoId)` → GET `.../pose-analysis`

Error mapping follows the existing `apiInterceptor` conventions (404/409/503 → typed `ApiError`;
503 = "LLM unavailable", surfaced with a retry affordance).

### 2. Tab rendering

- **SummaryTab** — new "Critical insight" card (`critical_insight`) + "Next session focus"
  directive under the existing metric cards; loading skeleton while generating.
- **PlanTab** — primary source becomes the structured plan: 4 week-cards with focus + drill
  lists + `bail_strategy` safety card; falls back to the current `agent_reply` markdown parse
  when no coach payload exists yet.
- **PoseTab** — renders `action_step` as the primary call-to-action and
  `biomechanical_flaw`/`correction`/`aesthetic_feedback` alongside the existing issue callouts.

## Implementation Roadmap

### Phase A: DTOs + services (ticket PAIML-POLE-ANALYST-058)
- [ ] Models + pure DTO→view mappers under `features/analysis/models/` (framework-free, unit-tested).
- [ ] `AnalysisService` methods + typed error mapping.
- [ ] Unit specs for mappers + service (HttpTestingController).

### Phase B: Tabs rendering + fallbacks (ticket PAIML-POLE-ANALYST-059)
- [ ] SummaryTab / PlanTab / PoseTab consume the new models; skeletons for the generate path.
- [ ] PlanTab dual-source logic (structured payload first, legacy parser fallback).
- [ ] Unit tests per tab; Playwright E2E extension against a mocked-LLM backend.

## Quality Gates

- **Unit Tests:** `npx ng test --watch=false` — ≥ 80% coverage en `src/app`.
- **E2E:** Playwright contra `pixi run api` con DBs `_testing`; el LLM del backend se mockea en E2E.
- **Additional Checks:** lint + typecheck (`npx ng build`), sin subscription leaks
  (`takeUntilDestroyed`).

## Dependencies

- **Blocked By:** pole_api Phase 21 endpoints (PAIML-POLE-API-064).
- **Blocks:** none.

## Open Questions

- None — regeneration UX lives in the backend tickets; FE always calls the endpoint.
