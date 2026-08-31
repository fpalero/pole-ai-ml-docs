# Ticket: PAIML-POLE-API-076

## Title
[Application] Analyst chatbot tool `improvement_plan` — 4-week plan generation via chat

## Description
Phase 26 (PLAN_PHASE_26.md), tool #3. Exposes the Phase 21 `CoachService.plan(video_id,
target_trick, athlete_notes)` (4-week improvement plan, cached on the video doc as `coach_plan`)
as a sync chatbot tool, so the coach can ask "give me a plan to master <trick>" directly in the
analyst chat. Read-only adapter; the LLM work stays inside `CoachService` (already schema-validated
with retry).

## What to Do (Implementation Steps)
- [ ] `AnalystFacade.improvement_plan(video_id, target_trick, athlete_notes=None)` — cache-read
      first: if `videos.coach_plan` exists for the same `target_trick` return it as-is (no LLM
      call); otherwise call `CoachService.plan(video_id, target_trick, athlete_notes)` and persist
      via the service's own update. Map `CoachLLMError` / `VideoNotAnalyzedError` to structured
      `{"error": ...}`.
- [ ] Return the stored envelope `{target_trick, content, model, generated_at}` plus a
      `hint_to_agent` telling the agent to render the plan content as markdown and offer a
      `video_segment` block when the plan references frames.
- [ ] Register `ToolSpec(name="improvement_plan", mode="sync", ...)` in `analyst_chatbot/tools.py`,
      params `{video_id: string (required), target_trick: string (required), athlete_notes:
      string}`.
- [ ] Add one line to `ANALYST_SYSTEM_PROMPT` tool list.
- [ ] Tests: facade cache-hit (same target), cache-miss generation, different-target cache
      invalidation, LLM-unavailable structured error, tool registration.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Cache-first: repeated requests for the same target do not re-call the LLM.
- [ ] Never raises to the WS; structured errors for unanalyzed video / LLM degradation.
- [ ] `pixi run test-api` green; coverage ≥ 80% maintained.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: None
- **Blocked By**: Phase 21 (`CoachService.plan`, merged)

## Estimated Effort
- [S]
