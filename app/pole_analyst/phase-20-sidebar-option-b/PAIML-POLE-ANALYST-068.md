# Ticket: PAIML-POLE-ANALYST-068

## Title
[Features] Sidebar simplification (Option B) — remove Coach nav item and Upload button

## Description
Phase 20 (PLAN_PHASE_20.md). PO decision 2026-08-24: navigation is **side-menu only**; the side
menu ends up as `Dashboard ▾` group containing exactly `Library`, `Analysis`. Removes the `Coach`
nav item (chat pane is always visible on the left — redundant entry point) and the sidebar
`Upload Video` button (upload entry point remains the Library pane's drag&drop + button).

## What to Do (Implementation Steps)
- [ ] app.ts: drop `coach` from navItems + its onNavClick case; no other route regressions.
- [ ] SidebarComponent: remove upload-btn markup/handler/styles (keep component API surface minimal;
      remove now-dead uploadClick output if unconsumed elsewhere — grep before deleting).
- [ ] Update unit specs (app/sidebar): assert absence of Coach + upload, group intact.
- [ ] Update e2e sidebar-navigation.spec.ts accordingly (drop coach/upload assertions).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Sidebar renders Dashboard ▾ / Library / Analysis only; upload only in Library pane; chat pane
      unchanged and always visible.
- [ ] Suite green; build clean.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`; sidebar e2e spec

## Dependencies
- Blocks: PAIML-POLE-ANALYST-069 · Blocked By: none · Effort: [S]
