# Ticket: PAIML-POLE-ANALYST-072

## Title
[Chat] Render the 5 missing FE chat-card types (score_summary / phasic_feedback / metric_matrix / drills / quick_replies)

## Description
Phase 23 — see [PLAN_PHASE_23](../plan/PLAN_PHASE_23.md). `app/pole_analyst`: the chat pane
(`features/chat/components/chat-pane/chat-pane.component.ts`, inline template) falls into a `@default`
placeholder for `score_summary`, `phasic_feedback`, `metric_matrix`, `drills` and `quick_replies`.
Render all five as Stitch-styled cards/pills against the backend contract (`analyst_chatbot/blocks.py`,
`PAIML-POLE-API-087`, phase-28); block model already complete in `core/models/api.models.ts`
(`ChatAnswerBlock` union). Cover with unit tests.

## What to Do (Implementation Steps)
- [ ] In `chat-pane.component.ts` (or child card components): render `score_summary` card (Stitch Kinetic
      Score badge style, `score`/`max` + `classification` + optional `summary`).
- [ ] Render `phasic_feedback` card (rows with status chip: `Consistent` | `Needs Adjustment` |
      `Optimal Form`, `phase_title` + `description` + optional `timestamp`).
- [ ] Render `metric_matrix` card (optional `title` + table: `parameter`, `benchmark_target`,
      `recorded_value`, `variance`, `assessment`).
- [ ] Render `drills` card (`title` + `description` + `sets_reps`; `drill_id` for keying only).
- [ ] Render `quick_replies` pills (`replies: string[]`); pill click sends the text via
      `ChatbotService.sendMessage` (reuse the composer path, disable while state Thinking/Working).
- [ ] Style with design tokens (`app.scss`/`design-tokens`), WCAG 2.1 AA aria labels, no subscription
      leaks (`takeUntilDestroyed`); keep the `@default` placeholder for unknown types.
- [ ] Add/adjust unit specs for all five renderers (chat-pane specs or child card components), ≥ 80% coverage.
- [ ] Add "New conversation" reset action in the chat-pane header — clears local messages and starts a
      fresh WS session (disconnect + reconnect WITHOUT sending the resume frame / without session_id),
      per the analyst chatbot WS protocol. Must work from any state (Idle/Thinking/Working/Error), be
      disabled while Thinking/Working or no-op safe, include aria-label/WCAG styling with design tokens,
      and be covered by unit tests (chat-state / chat-pane spec).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Each block type renders its card when present in `agent_reply.blocks`.
- [ ] Unknown types keep the existing default placeholder (never raw JSON).
- [ ] Quick pill click sends the message; pills disabled while Thinking/Working.
- [ ] No subscription leaks (`takeUntilDestroyed`).
- [ ] Long-session guard: a reset round-trip yields a new ws_connection_id/session (no resume), and a
      40-question UI drive does not hit context saturation (questions after ~15 do not fall back) — reset
      between chunks.
- [ ] `npx ng test --watch=false` green, `npx ng lint` clean, `npx ng build` typecheck passes.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`
- [ ] `npx ng lint`
- [ ] `npx ng build`

## Dependencies
- **Blocks**: None
- **Blocked By**: None

## Estimated Effort
- [M]
