# Ticket: PAIML-POLE-API-082

## Title
[Application] Analyst chatbot tools `get_coach_summary` / `get_coach_pose` — read cached coach advice

## Description
Phase 26 (PLAN_PHASE_26.md), tool #9 (quick win). Adds two sync read-only chatbot tools that
surface already-generated coach advice cached on the video doc (Phase 21 envelopes): `coach_summary`
(performance summary) and `coach_pose` (text-only critical-pose breakdown). Pure cache reads — no
LLM calls; lets the coach ask "what did the coach say before?" and gives the agent grounding to
build on prior advice instead of regenerating it.

## What to Do (Implementation Steps)
- [ ] `AnalystFacade.get_coach_summary(video_id)` and
      `AnalystFacade.get_coach_pose(video_id)` — validate id; return the stored envelope
      `{content, model, generated_at}` (pose also `frame`) when present; structured
      `{"error": "no <field> for this video; run the analysis/coach endpoints first"}` otherwise.
- [ ] Add both to `ANALYST_TOOL_NAMES` and register `ToolSpec(name=..., mode="sync", ...)` in
      `analyst_chatbot/tools.py` (params `{video_id: string (required)}` each).
- [ ] Add one line each to `ANALYST_SYSTEM_PROMPT` tool list (keep the "N tools are the ONLY tools"
      sentence accurate — count grows by 2).
- [ ] Tests: facade cache-hit and cache-miss error for both tools, tool-registration tests.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Both tools are pure cache reads (no LLM call on any code path).
- [ ] Never raises to the WS; structured error when the envelope is absent.
- [ ] `pixi run test-api` green; coverage ≥ 80% maintained.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: None
- **Blocked By**: Phase 21 coach envelopes (`coach_summary`, `coach_pose`, merged)

## Estimated Effort
- [S]
