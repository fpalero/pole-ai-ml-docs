# Ticket: PAIML-POLE-ANALYST-005

## Title
[Test] Unit tests T1.x (layout, atoms, interceptor, state machine)

## Description
Write the Phase 1 unit test suite covering the shell layout, shared atoms, the error
interceptor, and the `ChatState` reducer.

## What to Do (Implementation Steps)
- [ ] Cover the shell layout render and top bar.
- [ ] Cover each shared atom's states.
- [ ] Cover the interceptor's `{detail}` → typed error mapping.
- [ ] Cover the `ChatState` reducer transitions.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `npx ng test --watch=false` passes.
- [ ] Coverage for Phase 1 code is ≥ 80%.

## Integration Tests to Run (Local Verification)
- [ ] N/A (unit-level; validates the building blocks for UC-04/UC-07).

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLE-ANALYST-002, PAIML-POLE-ANALYST-003, PAIML-POLE-ANALYST-004

## Estimated Effort
- [M]
