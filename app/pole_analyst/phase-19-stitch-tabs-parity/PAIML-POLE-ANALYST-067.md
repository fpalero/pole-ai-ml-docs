# Ticket: PAIML-POLE-ANALYST-067

## Title
[Features] Sidebar Upload button — investigate PO report "missing" and fix placement/visibility

## Description
Phase 19 (PLAN_PHASE_19.md). Code review shows `upload-btn "Upload Video"` exists in
SidebarComponent, yet the PO reports it missing. Investigate root cause (responsive hiding?
collapsed-group interaction after -063? state-dependent rendering? stale bundle at time of report),
fix so the upload affordance is always visible per the Stitch design, and add regression specs.

## What to Do (Implementation Steps)
- [ ] Reproduce: serve app, verify visibility across breakpoints/states; identify condition hiding it.
- [ ] Fix root cause (placement/visibility per design); ensure it composes with the collapsible
      Dashboard group (-063) without being nested inside it.
- [ ] Regression spec asserting button presence across states/breakpoints (unit) + e2e assertion.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Upload visibly present in sidebar in all supported viewports/states.
- [ ] Root cause documented in ticket comment/PR body.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`; sidebar e2e spec

## Dependencies
- **Blocks**: none · **Blocked By**: PAIML-POLE-ANALYST-063 (sidebar structure lands first)
- Effort: [S]
