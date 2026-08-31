# Ticket: PAIML-POLE-AGENT-004

## Status
✅ DONE — Implemented

## Title
[Application] Enforce Crop → Confirm → (Shift → Confirm)* → Analyze →
(Correct?) prompt flow

## Description
The current `ReActAgent` system prompt is advisory only — the LLM may skip
confirmation steps or jump straight to analysis.  This is a reliability risk
(PLAN §6: "LLM prompt drift — agent skips confirmation").

Strengthen the `ReActAgent` so the conversation workflow is enforced
programmatically, not just suggested by the prompt:

1. **Crop must happen before Analyze** — if the LLM requests analysis without
   a confirmed crop, the agent injects a guardrail message demanding a crop
   first.
2. **Confirmation is required** — after every crop/shift, the agent must
   explicitly ask the user to confirm before proceeding.
3. **Shift loop** — user may say "shift by Xs" multiple times; each shift
   resets the `confirmed` flag.
4. **Analyze then Correct?** — after analysis, the agent offers an optional
   correction step.
5. **Max iterations** — the ReAct loop already has `max_iterations`; ensure
   guardrail messages count toward the budget and the agent exits gracefully
   when exhausted.

Leverage `ChatbotSession.confirmed` (from PAIML-POLE-AGENT-001) to track
confirmation state between turns.

## What to Do (Implementation Steps)
- [x] Refine the system prompt in `ReActAgent` to make the workflow
  non-negotiable (crop → confirm → shift → confirm → analyze).
- [x] Add programmatic guardrails in the ReAct loop: before calling
  `analyze`, check that `session.confirmed == True` and `session.current_crop`
  is set.
- [x] After a `crop` or `shift` tool call, set `confirmed = False` and append
  an agent message asking for confirmation.
- [x] After user confirms, set `confirmed = True` and proceed.
- [x] After analysis completes, append an optional `correct?` prompt.
- [x] Add guardrails to `max_iterations` — if budget exhausted, output
  fallback message "I could not complete the analysis; please try again
  with a shorter video".
- [x] Unit-test the guardrail logic with mocked tool outputs and session
  states.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] `CropTool` call without prior confirmation is rejected by guardrail.
- [x] After a shift, `confirmed` is reset and agent asks for re-confirmation.
- [x] `analyze` only proceeds when `confirmed == True`.
- [x] `max_iterations` exhaustion yields a graceful fallback, not a crash.
- [x] Unit tests cover: skip-confirmation rejection, shift-reset-confirm,
  max-iterations fallback, correct? prompt after analysis.
- [x] No regressions in `test-chatbot`.

## Integration Tests to Run (Local Verification)
- [x] Run UC-AG-03: Crop → shift → confirm → analyze multi-step — verify
  confirmation enforcement works end-to-end.
- [x] Run UC-AG-04: Crop fails → verify guardrail doesn't interfere with
  error handling.
- [x] `pixi run test-chatbot` — all tests pass.

## Dependencies
- **Blocks**: PAIML-POLE-AGENT-008
- **Blocked By**: PAIML-POLE-AGENT-001

## Estimated Effort
- [M]
