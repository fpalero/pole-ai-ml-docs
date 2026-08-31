# Ticket: PAIML-POLE-ANALYST-063

## Title
[Features] Sidebar collapsible Dashboard group (Stitch structural parity)

## Description
Phase 18 (PLAN_PHASE_18.md). The Stitch design renders the side menu as a collapsible
`Dashboard ▾` group containing the navigation entries; the app renders a flat list. Restructure
`SidebarComponent` accordingly WITHOUT changing navigation targets (Library/Analysis routes;
Coach → chat pane per Phase 17; Dashboard itself is only the collapsible group header, not a route).

## What to Do (Implementation Steps)
- [x] Group header `Dashboard` as `<button>` with rotating `expand_more` icon, `aria-expanded`,
      `aria-controls`; children indented beneath; default expanded; toggle via signal.
- [x] Keep existing item order/labels/icons: Library, Analysis, Coach (no Settings).
- [x] Active-item highlight preserved for child items; header itself not a route.
- [x] Update `sidebar.component.spec.ts`, `app.spec`/page specs touching nav markup, and
      Playwright `sidebar-navigation` spec selectors for grouped DOM.
- [x] Visual check vs Stitch screen (indentation, chevron, spacing tokens).

## Iteration 2 (QA design round follow-ups)
- [x] Parameterize the group: `groupLabel` / `groupGroupId` inputs on `SidebarComponent`
      (defaults keep prior behavior identical). Fixes the Open/Closed violation of the
      hardcoded "Dashboard" label and the duplicate-DOM-id hazard of the hardcoded
      `sidebar-dashboard-group` id. `app.ts` binds both explicitly.
- [x] Focus management on collapse: if focus sits inside the group container when it
      collapses, move focus to the group header button (keyboard UX).
- [x] Docs hygiene: fixed stale "Dashboard/Coach → chat pane" description (header is not
      a route); noted the append-only UC numbering convention for e2e `UC-Sidebar-10`.

## Iteration 3 (QA round-2 approved refactor)
- [x] Centralize expand/collapse mutation into a private `setExpanded(expanded)` that owns the
      move-focus-to-header-on-collapse invariant; `toggleGroup()` delegates (zero behavior change).
- [x] Companion a11y: header id derived as `<groupGroupId>-header`; items container gets
      `aria-labelledby` pointing at it so SRs announce the group name.
- [x] Prettier hygiene: wrapped the >100-char `@angular/core` import line in
      `sidebar.component.ts`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] Sidebar matches Stitch structure: collapsible Dashboard group + nested items.
- [x] All specs/E2E green after selector updates; `ng build` clean.
- [x] No subscription leaks; keyboard operable (Enter/Space toggles group, Tab reaches children).

## Integration Tests to Run (Local Verification)
- [x] `npx ng test --watch=false`
- [x] `npx playwright test e2e/sidebar-navigation.spec.ts`

## Dependencies
- **Blocks**: none
- **Blocked By**: none

## Estimated Effort
- [S]
