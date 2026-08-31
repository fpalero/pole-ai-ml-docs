# Ticket: PAIML-POLE-ANALYST-024

## Title
[Test] Unit tests T5.x (error branches, reconnect idempotency)

## Description
Unit-test the edge/error handling: invalid-upload errors, no-skeleton messaging, and reconnect
idempotency (no duplicate session/messages after resume).

## What to Do (Implementation Steps)
- [ ] Cover invalid-upload inline error + guidance.
- [ ] Cover no-skeleton message + badge retention.
- [ ] Cover reconnect idempotency (resume does not duplicate messages).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `npx ng test --watch=false` passes.
- [ ] Coverage for Phase 5 code is ≥ 80%.

## Integration Tests to Run (Local Verification)
- [ ] N/A (unit-level; validates UC-05/UC-06/UC-04 edge paths).

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLE-ANALYST-021, PAIML-POLE-ANALYST-022, PAIML-POLE-ANALYST-023

## Estimated Effort
- [M]
