# Ticket: PAIML-POLE-ANALYST-073

## Title
[Chat] Render failed turns distinctly (error bubble/chip + retry) + adopt image endpoint URLs

## Description
Phase 24 — see [PLAN_PHASE_24](../plan/PLAN_PHASE_24.md). FE consumer of
`PAIML-POLE-API-093` item (d): backend ABANDONED/error turns now emit an explicit,
machine-readable error status on the `agent_reply` frame instead of chip `Completed` +
generic fallback `md` ("I'm having trouble understanding…"). Tester evidence (local, not
committed): `/tmp/opencode/tool08-repro/tool08-frames.json` (`"chipFinal": "Completed"`,
fallback `agent_reply` with `tool_calls: []`) and `/tmp/opencode/staging-battery/summary.json`
(TOOL-08 `rendered: []`, TOOL-18/TOOL-19 fallback-text notes).

Today the chat pane (`features/chat/components/chat-pane/chat-pane.component.ts`, inline
template; state in `ChatbotService`/`ChatState`) renders those failed turns as a normal
completed `md` bubble, so users cannot tell a failure from an answer and have no retry path.
Render them distinctly, and adopt the new endpoint URLs for `image` blocks from
`PAIML-POLE-API-093` item (a) (verify-only if `src` becoming an HTTP(S) URL needs no
renderer change).

## What to Do (Implementation Steps)
- [ ] Branch on the backend error signal from `PAIML-POLE-API-093(d)` (`agent_reply` error
      status/code): failed turns render an error bubble/chip (distinct Stitch error styling
      via design tokens, not the `Completed` state chip) instead of the generic fallback `md`.
- [ ] Add a retry affordance on the error bubble (re-send the same message via
      `ChatbotService.sendMessage`, reusing the composer path; disabled while state
      Thinking/Working); keep the failed turn in history as an error (never rewrite it as a
      normal answer).
- [ ] Error bubble/chip carries WCAG 2.1 AA aria-labels (e.g. `aria-label="chat error"`,
      `aria-live` as per existing chat-pane conventions); style with design tokens
      (`app.scss`/`design-tokens`); no subscription leaks (`takeUntilDestroyed`).
- [ ] Adopt endpoint URLs for `image` blocks: verify the existing `image` renderer loads the
      `PAIML-POLE-API-093(a)` endpoint URL `src` (auth/proxy via `ng serve` proxy config if
      needed); change the renderer only if a container-path assumption breaks it. Confirm no
      `/data/` path rendering remains on the FE side.
- [ ] Add/adjust unit specs (chat-pane / chat-state specs): error-signal → error bubble/chip +
      retry enabled/disabled states; `image` with endpoint URL renders; ≥ 80% coverage.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] A forced-error/ABANDONED turn (backend error status) renders an error bubble/chip with
      retry affordance — never chip `Completed` + generic fallback `md`.
- [ ] Retry re-sends via the composer path; disabled while Thinking/Working.
- [ ] Aria-labels + design-token styling asserted; no subscription leaks.
- [ ] `image` blocks with endpoint-URL `src` load in the chat pane (verify-only if no
      renderer change was needed); no `/data/` strings rendered.
- [ ] `npx ng test --watch=false` green, `npx ng lint` clean, `npx ng build` typecheck passes.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`
- [ ] `npx ng lint`
- [ ] `npx ng build`
- [ ] Manual/Playwright spot check: forced-error turn shows the error bubble + retry works;
      TOOL-04/TOOL-18-class `image` turns load their endpoint URLs.

## Dependencies
- **Blocks**: None
- **Blocked By**: `PAIML-POLE-API-093` (backend (d) error signal + (a) image endpoint URLs;
  FE work starts against that contract with mock/stub until wired in E2E).

## Estimated Effort
- [M]
