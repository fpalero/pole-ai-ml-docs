# Ticket: PAIML-POLE-ANALYST-071

## Title
[Chat] FE never renders raw JSON / technical data (chat + insights defensive fallback)

## Description
Phase 22. `app/pole_analyst`: (a) `chat-message.ts` / `chat-pane.component.ts`: when a
frame/history payload has no usable `blocks` or its content looks like a raw JSON
array/object, decode it into md blocks instead of rendering the raw text; raw JSON must
never appear in a bubble; (b) `tips-insights-panel.component.ts` / `coach-insights.ts`:
ensure no `zScore` or metric id is shown to the user (backend supplies plain
`explanation`; verify it passes through); (c) update component specs.

## What to Do (Implementation Steps)
- [ ] In `chat-message.ts` / `chat-pane.component.ts`: when a frame/history payload has
      no usable `blocks` or its content looks like a raw JSON array/object, decode it
      into md blocks instead of rendering the raw text.
- [ ] In `tips-insights-panel.component.ts` / `coach-insights.ts`: ensure no `zScore` or
      metric id is shown to the user (backend supplies plain `explanation`; verify it
      passes through).
- [ ] Update component specs (`.spec.ts`) to cover raw-JSON payload → formatted text/cards
      and insights panel plain-explanation-only cases.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] With mocked raw-JSON payloads, the UI shows formatted text/cards, never raw JSON.
- [ ] Insights panel shows plain explanation only.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`

## Dependencies
- **Blocks**: None
- **Blocked By**: None

## Estimated Effort
- [S]
