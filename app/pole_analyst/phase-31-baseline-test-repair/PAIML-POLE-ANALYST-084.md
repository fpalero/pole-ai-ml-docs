# Ticket: PAIML-POLE-ANALYST-084

## Title
Fix smoke E2E drift: welcome quick-reply pills count 6 → 7

## Description
`app/pole_analyst/e2e/smoke.spec.ts` (E2E-1 / empty-library) asserts `.quick-reply-pill` has count **6**, but the source `app/pole_analyst/src/app/features/chat/models/chat-message.ts` (lines 709–719) renders **7** `quick_replies` (a 7th "What should I work on next?" was added to the welcome message). The spec is stale → the remote E2E run fails `expected 6, resolved to 7`. Fix the spec expectation (source is authoritative).

## Repository
`pole-ai-ml`

## Affected
- `app/pole_analyst/e2e/smoke.spec.ts` (line ~44 `toHaveCount(6)`)

## What to Do (Implementation Steps)
- [ ] Step 1: Update the `.quick-reply-pill` assertion from `toHaveCount(6)` to `toHaveCount(7)`
- [ ] Step 2: Confirm the 7th pill ("What should I work on next?") is also asserted or intentionally unasserted (do not add coverage beyond the count fix unless trivial)
- [ ] Step 3: No production-code change

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `npx playwright test e2e/smoke.spec.ts -g "empty library"` passes (no 6→7 count failure)
- [ ] No production source change; spec-only

## Dependencies
- **Blocks:** None
- **Blocked By:** None
- **Related:** PAIML-POLE-ANALYST-083 (welcome message expansion)