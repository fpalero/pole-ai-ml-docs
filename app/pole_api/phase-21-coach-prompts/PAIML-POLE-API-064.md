# Ticket: PAIML-POLE-API-064

## Title
[Application] Coach REST endpoints — coach-summary / coach-plan / pose-analysis

## Description
Phase 21 (§3, PLAN_PHASE_21.md Phase C). Expose the three one-shot coach actions as REST
endpoints in `analysis/controllers/videos.py`. Semantics: first call generates + caches on the
video doc; subsequent calls return the cached payload. LLM-down / not-analyzed degrade to
structured error details — never a crash.

| Endpoint | Método | Descripción |
| :--- | :--- | :--- |
| `/api/analysis/videos/{video_id}/coach-summary` | GET | Generate-or-return cached performance summary |
| `/api/analysis/videos/{video_id}/coach-plan` | POST | Generate plan for `target_trick` (body) |
| `/api/analysis/videos/{video_id}/pose-analysis` | GET | Generate-or-return cached pose breakdown |

## What to Do (Implementation Steps)
- [ ] Pydantic response models in `analysis/schemas.py`: `CoachSummaryOut`
  (`{summary, critical_insight, focus_next_session}`), `ImprovementPlanOut`
  (`{issue, weeks[4]: {week, focus, drills[]}, bail_strategy}`), `PoseAnalysisOut`
  (`{biomechanical_flaw, correction, aesthetic_feedback, action_step}`).
- [ ] Wire routes to `CoachService` methods (PAIML-POLE-API-063); reuse the shared `OllamaLLM`
  instance pattern from `main._build_analyst_chatbot_deps`.
- [ ] Regeneration UX (decide at this ticket): support `?refresh=true` on GET endpoints to force
  regeneration (last-write-wins overwrite).
- [ ] Error contracts: `409/422` structured detail when video not analyzed ("run the analysis
  pipeline first"); `503`-shaped structured detail on LLM unavailable / invalid JSON degradation;
  cached payload still served when present (UC-C6).
- [ ] Route-order guard: declare static path segments before any `{video_id}` catch-all patterns.
- [ ] Integration tests with mocked LLM: happy paths (UC-C1..C4), cached read (UC-C2),
  video-not-analyzed (UC-C5), LLM-unavailable (UC-C6), regenerate flow.
- [ ] Update `docs/diagrams/pola_api/CLASSES.md` §6 + `POLE-API.md` endpoint list.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] All three endpoints return schema-valid JSON grounded in stored analysis data.
- [ ] Cached-read semantics verified (no LLM call on second GET — observable via mock call count).
- [ ] Pose endpoint provably never reads/sends image bytes.
- [ ] Not-analyzed → 409/422; LLM-down → 503 with structured detail; no 500s.
- [ ] Coverage ≥ 80% for new controller/schema code.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; LLM always mocked).

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-058 (FE coach tabs consume these endpoints)
- **Blocked By**: PAIML-POLE-API-063

## Estimated Effort
- [M]
