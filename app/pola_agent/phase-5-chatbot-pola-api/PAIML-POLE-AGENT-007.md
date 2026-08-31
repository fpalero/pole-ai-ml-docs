# Ticket: PAIML-POLE-AGENT-007

## Status
✅ DONE — Implemented

## Title
[Infrastructure] Metrics collection — tool latency and LLM token usage

## Description
Visibility into chatbot performance is critical for tuning and debugging.
Implement instrumentation that captures:

- **Tool latency** — wall-clock duration of each tool invocation (`crop`,
  `shift`, `analyze`, `correct`) in milliseconds.
- **LLM token usage** — prompt tokens, completion tokens, and total tokens
  per `ReActAgent` turn (extracted from `OpenCodeLLMClient` response).
- **Session metrics** — total messages, total tool calls, total LLM turns,
  session duration.

Metrics should be emitted as structured logs (JSON to stdout) and optionally
to a Prometheus-compatible endpoint for scraping.  Use the existing
`pole_chatbot` config module for opt-in flags.

This ticket covers the **collection** side only; dashboarding or alerting is
out of scope.

## What to Do (Implementation Steps)
- [x] Add `collect_metrics: bool` to `ChatbotSettings` (env
  `CHATBOT_COLLECT_METRICS`, default `false`).
- [x] Implement a `MetricsCollector` class with methods:
  `record_tool_latency(tool_name, ms)`, `record_llm_tokens(prompt, completion)`,
  `record_session_event(session_id, event)`.
- [x] Decorate / wrap tool invocations in `ReActAgent` to capture latency.
- [x] Extract token counts from `OpenCodeLLMClient` response
  (`usage.prompt_tokens`, `usage.completion_tokens`).
- [x] Emit JSON-structured log lines (level INFO) prefixed with
  `[chatbot-metrics]`.
- [x] Unit-test the `MetricsCollector` with mock log capture.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] Tool latency is logged in ms per invocation.
- [x] LLM token counts are logged per agent turn.
- [x] Metrics are opt-in via config flag; zero overhead when disabled.
- [x] JSON log output can be parsed by `jq`.
- [x] Unit tests verify metric emission format and values.
- [x] No regressions in existing chatbot test suite.

## Integration Tests to Run (Local Verification)
- [x] Enable `CHATBOT_COLLECT_METRICS=true`; run UC-AG-01 — verify
  `[chatbot-metrics]` log lines appear with tool latency and token counts.
- [x] `pixi run test-chatbot` — all tests pass.

## Dependencies
- **Blocks**: PAIML-POLE-AGENT-008
- **Blocked By**: None

## Estimated Effort
- [S]
