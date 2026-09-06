# Ticket: PAIML-POLE-API-087

## Title
[Chatbot] Chat replies never leak raw JSON (reply normalization + history replay)

## Description
Phase 28. `app/pole_api/src/analyst_chatbot/`: every turn's wire `reply` must be readable markdown (synthesized from the parsed blocks, e.g. via `blocks_to_text` / md synthesis) instead of the raw LLM JSON-array string; keep the structured `blocks` field for rich rendering. Persisted chat history and `session_resumed` replay must expose plain-text `content`, never the raw JSON. Verify the legacy `pole_fe` chatbot page (renders `reply`) also benefits.

## What to Do (Implementation Steps)
- [ ] Normalize every turn's wire `reply` in `analyst_chatbot/services.py` and `analyst_chatbot/router.py` (agent_reply construction, `_non_system_messages`) to readable markdown synthesized from the parsed blocks (e.g. via `blocks_to_text` / md synthesis) instead of the raw LLM JSON-array string.
- [ ] Keep the structured `blocks` field for rich rendering.
- [ ] Fix persisted chat history and `session_resumed` replay to expose plain-text `content`, never the raw JSON; fix `_format_history_for_client` in `app/pole_api/src/chatbot/router.py`.
- [ ] Verify the legacy `pole_fe` chatbot page (renders `reply`) also benefits.
- [ ] Add/update tests in `app/pole_api/tests/test_analyst_chatbot*.py` to assert `reply` is markdown and history content is non-JSON.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] No code path renders raw JSON; fresh answer and session resume both show markdown.
- [ ] Tests assert `reply` is markdown and history content is non-JSON.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: None
- **Blocked By**: None

## Estimated Effort
- [S]
