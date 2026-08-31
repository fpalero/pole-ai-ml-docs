# Ticket: PAIML-POLE-API-071

## Title
[Frontend] Analysis completion notification + chat auto-suggestion

## Description
Phase 23 (§2). When analysis completes, surface the result to the user in two ways:

1. **FE notification** — simplified notification banner (not full bell port from pole_fe) that
   appears when analysis job transitions to `done`. Shows deviation count and trick label.
2. **Chat auto-suggestion** — chatbot auto-sends an `agent_reply` message with deviation summary
   and a proactive question ("Want me to break down the pose mechanics?").

## What to Do (Implementation Steps)
- [ ] Create `AnalysisNotificationComponent` (inline, standalone) — a dismissible banner that
  appears at the top of the analysis detail page when a new analysis completes.
  - Shows: "Analysis complete — detected {trick_label} with {N} deviations."
  - Auto-dismiss after 8s or manual close.
- [ ] Wire into `AnalysisDetailPage` — listen to analysis job `done` event, show notification.
- [ ] In `AnalyzeWorker._run()`, after insights computation, push a chatbot message:
  - Use `AnalystFacade` or direct WS message to send `agent_reply` with deviation summary.
  - Message format: "Analysis complete for {filename}. I detected {N} frames with deviations.
    Want me to break down the pose mechanics?"
- [ ] Unit tests for notification component.
- [ ] Unit test for chat auto-suggestion in worker.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Notification banner appears on analysis completion with trick label + deviation count.
- [ ] Banner auto-dismisses or can be manually closed.
- [ ] Chatbot sends auto-suggestion message after analysis.
- [ ] Auto-suggestion only fires when there are deviations (|z| > 2).
- [ ] Unit tests pass.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-analyst` (FE tests).
- [ ] `pixi run test-api` (backend worker tests).

## Dependencies
- **Blocks**: None
- **Blocked By**: PAIML-POLE-API-069 (insights must exist for deviation count)

## Estimated Effort
- [M]
