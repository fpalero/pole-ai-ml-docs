# Ticket: PAIML-POLE-ANALYST-075

## Title
[Chat] Sanitize tool-chip display args (no server paths inside tool chips)

## Description
Phase 24 — see [PLAN_PHASE_24](../plan/PLAN_PHASE_24.md). FE display follow-up
from the staging QA gate-2 rerun (tester evidence, local, not committed):
`/tmp/opencode/staging-gate2/TOOL-06-SUB.json` + `summary.json`.

Today the chat pane renders the tool chip with raw tool arguments: the
TOOL-06-SUB turn (crop, handspring variant) shows `bubbleHead` ending in
`crop` + `/data/uploads/analys…` — a container-local server path inside the
crop tool chip. Backend prose/result stripping (`PAIML-POLE-API-093(b)`,
`PAIML-POLE-API-096` F2-backend) does not cover the FE chip rendering path, so
the chip must sanitize its own display args.

## What to Do (Implementation Steps)
- [ ] Sanitize tool-chip display args in the chat pane (same component/state as
  `PAIML-POLE-ANALYST-073`): never render absolute server paths
  (`/data/…` or any container-local prefix) inside a tool chip — show the
  tool name + human arguments only (e.g. `crop · 4s–7s`), dropping or
  basename-ing path-like args.
- [ ] Cover all tool chips (not just crop): `extract_frames`, `crop`,
  coach tools — one shared sanitize helper with unit specs.
- [ ] Keep chip behavior otherwise unchanged (states, aria-labels, retry per
  `PAIML-POLE-ANALYST-073`); style with design tokens; no subscription leaks
  (`takeUntilDestroyed`).
- [ ] Add/adjust unit specs: path-like chip args render sanitized; ≥ 80% coverage.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] A TOOL-06-SUB-class (crop) turn renders its tool chip with no server-path
  segment — no `/data/` strings anywhere in the chat pane.
- [ ] All tool chips share the sanitize path (no per-tool bypass).
- [ ] `npx ng test --watch=false` green, `npx ng lint` clean, `npx ng build` typecheck passes.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`
- [ ] `npx ng lint`
- [ ] `npx ng build`
- [ ] Manual/Playwright spot check: crop-turn chip shows human args only.

## Dependencies
- **Blocks**: None
- **Blocked By**: None (display-only; backend keeps emitting full args).
  Related: `PAIML-POLE-API-096` (F2-backend strip — sibling fix on the backend
  side), `PAIML-POLE-ANALYST-073` (same component/state).

## Estimated Effort
- [S]
