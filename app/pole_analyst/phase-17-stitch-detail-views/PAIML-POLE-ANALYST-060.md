# Ticket: PAIML-POLE-ANALYST-060

## Title
[Features] Video Library Filter Modal (Stitch screen parity — status filters)

## Description
Phase 17 Phase A (PLAN_PHASE_17.md). Implements the *Persistent Chat – Video Library Filter
Modal* Stitch screen **strictly as designed**: a "Filter Videos" modal opened from the history
table's `filter_list` button, containing exactly — Analyzed checkbox, Not analyzed checkbox,
`Clear all`, `Apply Filters`, close (X).

## What to Do (Implementation Steps)
- [ ] `LibraryFilterModalComponent` (standalone, signal inputs/outputs; focus trap + ESC dismiss;
      close X per design).
- [ ] Status checkboxes: Analyzed / Not analyzed (both unchecked = All); multi-select OR semantics.
- [ ] Footer actions per design: `Clear all` (left) + primary `Apply Filters`.
- [ ] Wire trigger button (`filter_list`) into the analysis-history toolbar; applied state reflected
      in the table; compose with the existing client-side filename search.
- [ ] Empty-state copy when nothing matches; unit specs: combinations, clear, apply, a11y trap.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Modal matches the Stitch screen element-for-element (status checkboxes only — no extra
      fields beyond the design).
- [ ] Filters compose with existing search; table updates on Apply.
- [ ] No regression on history-table specs.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-analyst`

## Dependencies
- **Blocks**: none
- **Blocked By**: none

## Estimated Effort
- [S]
