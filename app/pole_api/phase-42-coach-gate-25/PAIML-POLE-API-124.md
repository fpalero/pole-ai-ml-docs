# Ticket: PAIML-POLE-API-124

## Title
FE: render `progress_matrix` card + resilient image blocks (PR-01..05, TP-05)

## Status
📋 PLANNED — will be implemented FIRST (owner-ordered). Part of the
phase-42 residuals split after the post-PR-#322 staging run
(`RUN_ID sample5-e743e61-20260912-083119`, images `e743e61` = PR #322 merge,
FC1–FC6 landed; score **13/25, GATE FAIL**, bar 5/5 per flow). Judge:
`<feature-wt>/app/pole_analyst/test-results/coach-150q/sample5-e743e61-20260912-083119/coach-150q-judge.md`,
transcript `coach-150q-transcript.jsonl`. The 12 fails split into exactly 3
classes → tickets 124/125/126. Gate stays 🟡 PARTIAL until full 25/25.

## Description

Two distinct FE gaps make 6 SAMPLE-5 turns fail even though the backend reply
is already correct.

### PR-01..05 — FE never renders the `progress_matrix` block (5/5 progress flow fail)

Gate case evidence (COACH7-PR-01, PR-02, PR-03, PR-04, PR-05): the backend is
ALREADY correct on this staging image — replies carry
`block_types=["md","progress_matrix","analysis_link"]`,
`tool_call_names=["get_progress_matrix"]`, and the reply text is present
("Progress on handspring: 0/5 gates met…"). The failure assertion is the
spec's `locator('.bubble-assistant').last().locator('.matrix-card')`
`toBeVisible` timeout (20s) — the block is emitted but never painted.

Root cause:
`app/pole_analyst/src/app/features/chat/components/chat-pane/chat-pane.component.ts`
`@switch (block.type)` (line 126) has a `@case ('metric_matrix')` (line 238,
renders `.matrix-card`) but **no `progress_matrix` case** → the FE renders
nothing for the block → `.matrix-card` never appears in the DOM.

Fix: add a `progress_matrix` render case reusing the existing
`.matrix-card`/`.matrix-table` styles (lines 860-900) to render title + table,
and preserve the `analysis_link` block as-is. Add/adjust FE unit tests in
`chat-pane.component.spec.ts` covering the new case and proving no regression
on `metric_matrix`/other block types.

### TP-05 — broken image block: JWT minted at reply-build expires before browser fetch

Gate case evidence (COACH7-TP-05, training_plan): 8 RAG `tool_calls` OK, reply
present, blocks include `image`. The failure is a broken
`<img src="/api/images/<hash>?token=<JWT>">` — the token is minted when the
reply is built, then expires before the browser's fetch → **401**. Tester
Case C confirmed the SAME hash serves 200 with a FRESH token → asset is
healthy; the failure is token lifetime/refresh, not content.

Fix (owner decision pending — ticket documents both options, default
documented below):
- **(A) FE-side re-mint/retry (default):** on image load error, mark the image
  block "expired/refreshing" and retry once with a re-minted token; if it
  fails again, degrade gracefully (placeholder, never a broken-`<img>`
  assertion). Add an FE unit test for the image-load-error path.
- **(B) Backend token-TTL extension/refresh:** extend media token TTL or serve
  a refreshable URL so tokens minted at reply-build outlive browser fetches.
  Requires a BE change + its own validation; only chosen if (A) proves
  insufficient.

Default documented fix = **(A)**.

## Files Affected
- `app/pole_analyst/src/app/features/chat/components/chat-pane/chat-pane.component.ts`
- `app/pole_analyst/src/app/features/chat/components/chat-pane/chat-pane.component.spec.ts`
- FE only; branch `feature/PAIML-POLE-API-124-fe-renderer-gaps`. No DB changes.

## Validation Plan
1. FE unit tests green (`ng test` / project test target).
2. Targeted battery re-run against the deployed staging backend (remote-backend
   env, see existing launch envs):
   `npx playwright test coach-150q.spec.ts --workers=1 -g "COACH7-(PR-0[1-5]|TP-05|GATE)"`
   → PR-01..05 and TP-05 flip to pass.
3. Full SAMPLE-5 gate **25/25** as phase acceptance (together with
   PAIML-POLE-API-125 and PAIML-POLE-API-126).

## Unit-Test Requirement
- [ ] `progress_matrix` block renders `.matrix-card` (title + rows); other
      block types unchanged (`metric_matrix` regression guard).
- [ ] Image load error retries/re-mints once, then degrades gracefully
      (placeholder, no broken `<img>`).

## Integration Tests
- [ ] Targeted battery `-g "COACH7-(PR-0[1-5]|TP-05|GATE)"` green on
      staging (remote-backend mode).
- [ ] Full SAMPLE-5 gate 25/25 (with 125/126).

## Acceptance Criteria
- [ ] PR-01..05 and TP-05 pass in the SAMPLE-5 gate.
- [ ] No regression on `metric_matrix`/`analysis_link`/other flows.
- [ ] Full SAMPLE-5 **25/25** (with 125/126).
- [ ] No DB changes.

## Dependencies
- **Blocked By**: none.
- **Blocks**: none (independent of 125/126).

## Estimated Effort
- [M]