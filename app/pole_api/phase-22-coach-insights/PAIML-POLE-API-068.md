# Ticket: PAIML-POLE-API-068

## Title
[Application] Coach insights endpoint + chatbot tool

## Description
Phase 22 (§4). Expose coach insights via REST endpoint and chatbot tool. The endpoint returns
pre-computed insights (or triggers computation if missing). The chatbot tool reads from DB and
returns structured data for the agent to present in chat.

## What to Do (Implementation Steps)
- [ ] Add `GET /api/analysis/videos/{video_id}/coach-insights` endpoint in `analysis/controllers/videos.py`.
- [ ] Response schema: `CoachInsightsResponse` with `perfect`, `adjustment`, `wrong` lists, each
  containing `metric`, `phase`, `frame`, `z_score`, `explanation`.
- [ ] Wire endpoint to `CoachInsightsService.ensure()`.
- [ ] Add `get_coach_insights` chatbot tool in `analyst_chatbot/tools.py`:
  - Input: `video_id` (required).
  - Output: structured JSON with insight counts + top 3 worst frames.
  - Registers in `AnalystFacade`.
- [ ] Unit tests: endpoint returns correct shape, chatbot tool returns correct data.
- [ ] Integration test: compute insights → GET endpoint → verify response.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `GET /coach-insights` returns structured insight data.
- [ ] Chatbot tool `get_coach_insights` returns insight summary.
- [ ] Both trigger computation if insights are missing.
- [ ] Unit tests pass for endpoint + tool.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).
- [ ] `pixi run test-chatbot` (chatbot tool tests).

## Dependencies
- **Blocks**: PAIML-POLE-API-070 (FE Summary tab fetches `/coach-insights`)
- **Blocked By**: PAIML-POLE-API-067

## Estimated Effort
- [M]
