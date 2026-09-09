# Ticket: PAIML-POLE-ANALYST-078

## Title
[Presentation] Question-card status chip (status ONLY on user question card)

## Description
Phase 27 — see [PLAN_PHASE_27](../plan/PLAN_PHASE_27.md). Remove the standalone
thinking bubble in the `pole_analyst` chat pane; render turn status ONLY as a
chip on the user question card that originated the turn.

States come from the backend via the existing WebSocket (no WS behavior change):
`ChatState` Idle|Thinking|Working|Completed|Error, derived from events
`connected` / `message_sent` / `job_started` / `job_progress` / `agent_reply` /
`error` in `src/app/core/chat-state/chat-state.ts`, consumed live via
`ChatbotService.state$` + `ChatbotSocketService`. Host component:
`src/app/features/chat/components/chat-pane/chat-pane.component.ts`.

Terminal rendering on the user card: `Completed` → "Answered ✓ + timestamp";
`Error` → error text + Retry button. Retry re-sends via the
`ChatbotService.sendMessage` composer path (disabled while Thinking/Working) —
contract reused from `PAIML-POLE-ANALYST-073`. This ticket supersedes the
thinking-bubble part of 073 (Phase 24 note: 073 error bubble overlaps) but keeps
its retry contract.

Constraints: reusable standalone component (future apps), company style tokens
(`app.scss`/`design-tokens`), English only, WCAG 2.1 AA aria-labels per state,
no subscription leaks (`takeUntilDestroyed`). Grounding: `chat-state.ts`,
`chatbot.service.ts`, `chat-pane.component.ts`; tickets
`PAIML-POLE-ANALYST-004/007/008`; Phase 24
([PLAN_PHASE_24](../plan/PLAN_PHASE_24.md)).

## ADR — why the chip moves to the question card
- **Context:** two surfaces showed status (standalone bubble + turn chip/bubble)
  and could disagree; the 073 error bubble overlapped content.
- **Decision:** single status surface — chip anchored to the user question card.
  No standalone bubble.
- **Alternatives:** keep bubble + chip (rejected — dual source of truth,
  overlaps); chip on agent reply (rejected — state belongs to the question while
  Thinking/Working, before any answer exists).
- **Consequences:** reusable chip component; terminal states render on the same
  user card (Answered ✓ + timestamp / error + Retry).

## What to Do (Implementation Steps)
- [ ] Remove the standalone thinking bubble from the chat pane; status renders
      only on the user question card (no second status surface remains).
- [ ] Create a reusable standalone status-chip component (e.g.
      `question-status-chip`) with `@Input() state: ChatState` (+ timestamp /
      error inputs); English-only labels; company design tokens only
      (`app.scss`/`design-tokens`).
- [ ] Wire live states from the existing `ChatbotService.state$`
      (Idle|Thinking|Working|Completed|Error per `chat-state.ts` event mapping);
      keep WS behavior unchanged (`ChatbotSocketService`); `takeUntilDestroyed`,
      no leaks.
- [ ] Render terminal `Completed` as "Answered ✓ + timestamp" on the user card.
- [ ] Render terminal `Error` as error text + Retry button on the user card;
      Retry re-sends via `ChatbotService.sendMessage` (composer path), disabled
      while Thinking/Working (073 retry contract).
- [ ] Add per-state WCAG 2.1 AA aria-labels (chip + Retry button; `aria-live`
      per existing chat-pane conventions).
- [ ] Add/adjust unit specs: UC-04 Idle→Thinking→Working→Completed on the user
      card; error + retry enabled/disabled states; aria-labels + design-token
      classes; ≥ 80% coverage.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] No standalone thinking bubble in the chat pane; status visible only on the
      user question card.
- [ ] Live transition Idle→Thinking→Working→Completed (UC-04) renders on the
      user card.
- [ ] `Completed` shows "Answered ✓ + timestamp" on the user card.
- [ ] `Error` shows error text + working Retry on the user card; Retry uses the
      composer path and is disabled while Thinking/Working.
- [ ] Reusable component, company tokens, English only, per-state aria-labels
      (AA), no subscription leaks.
- [ ] `npx ng test --watch=false` green, `npx ng lint` clean, `npx ng build`
      typecheck passes.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`
- [ ] `npx ng lint`
- [ ] `npx ng build`
- [ ] UC-04 spot check: Idle→Thinking→Working→Completed chip transitions on the
      user card; forced-error turn shows error text + Retry works.

## Dependencies
- **Blocks**: None.
- **Blocked By**: None.
- **Related**: `PAIML-POLE-API-093` (backend error signal, external) and
  `PAIML-POLE-ANALYST-073` (retry contract reused; 078 supersedes its
  thinking-bubble part).

## Estimated Effort
- [M]
