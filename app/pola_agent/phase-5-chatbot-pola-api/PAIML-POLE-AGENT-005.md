# Ticket: PAIML-POLE-AGENT-005

## Status
✅ DONE — Implemented

## Title
[Application] Graceful LLM off-script handling — parse errors, max iterations,
rephrase

## Description
The LLM may produce malformed tool-call JSON, hallucinate non-existent tools,
or exceed the iteration budget.  Currently these failures bubble up as raw
exceptions or unhelpful error messages to the user.

Implement a robust off-script handler in `ReActAgent` that:

1. **Parse errors** — when the LLM response cannot be parsed as a valid tool
   call or plain text, catch the error, log it, and ask the LLM to rephrase.
2. **Unknown tools** — when the LLM requests a tool not in the `ToolRegistry`,
   reply with available-tools summary and ask the LLM to retry.
3. **Max iterations fallback** — when `max_iterations` is reached, return a
   pre-defined fallback message (not the raw last LLM output) and close the
   session with a clear status.
4. **Rephrase loop** — allow at most 2 rephrase attempts; on the 3rd failure,
   return fallback advice and set session to error state.

These handlers protect the user experience from LLM non-determinism and align
with risk mitigations in PLAN §6.

## What to Do (Implementation Steps)
- [x] Add `ToolParseError` to `pole_chatbot.exceptions` (or reuse existing).
- [x] In `ReActAgent._handle_tool_call`, wrap JSON parsing in try/except;
    on error, emit "I didn't understand that. Could you rephrase?" to the
    LLM and decrement a `rephrase_budget`.
- [x] In `ToolRegistry.invoke`, raise `UnknownToolError` for unrecognised
    tool names; agent catches it and replies with the tool list.
- [x] Implement `_handle_iteration_exhaustion`: pre-defined fallback message
    (e.g. "I'm having trouble understanding. Please try again with a
    shorter description."), mark session `ABANDONED` or `ERROR`.
- [x] Wire `rephrase_budget` (default 2) into the agent config; track it
    across the ReAct loop.
- [x] Unit-test each failure path: parse error → rephrase, unknown tool →
    retry, 3rd failure → fallback, max iterations → fallback.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] Malformed JSON LLM response yields "rephrase" prompt, not a 500.
- [x] Unknown tool request yields available-tools list and retry.
- [x] Third consecutive parse/unknown-tool failure returns fallback message.
- [x] `max_iterations` exhaustion returns pre-defined fallback, not raw LLM
    output.
- [x] Each handler is covered by a dedicated unit test.
- [x] Existing `test-chatbot` suite still passes.

## Integration Tests to Run (Local Verification)
- [x] Run UC-AG-05: LLM unavailable → fallback advice (mock LLM endpoint
    returning 503).
- [x] Mock LLM returning garbage JSON — verify rephrase+fallback loop.
- [x] `pixi run test-chatbot` — all tests pass.

## Dependencies
- **Blocks**: PAIML-POLE-AGENT-008
- **Blocked By**: PAIML-POLE-AGENT-001

## Estimated Effort
- [S]
