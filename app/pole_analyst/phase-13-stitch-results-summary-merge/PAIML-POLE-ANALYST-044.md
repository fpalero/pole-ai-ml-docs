# PAIML-POLE-ANALYST-044 — Remove Results tab, update AnalysisTabId

## Meta
- **Project:** pole_analyst
- **Phase:** 13 — Stitch Design: Results→Summary merge + Tab Reorder
- **Status:** TODO
- **Blocks:** PAIML-POLE-ANALYST-045
- **Blocked By:** PAIML-POLE-ANALYST-043

## Description

Remove the standalone Results tab and update the tab configuration to match the Stitch design:
4 tabs: Summary | Histogram | Pose | Plan.

### Tasks
- [ ] Remove `ResultsView` component and its spec file.
- [ ] Remove `'Results'` from `AnalysisTabId` union type in `analysis-detail.page.ts`.
- [ ] Update default tab from `'Results'` to `'Summary'`.
- [ ] Update `TabBar` tabs to: Summary | Histogram | Pose | Plan.
- [ ] Remove any references to ResultsView in the detail page template.
- [ ] Update unit tests that reference the Results tab.

### Acceptance Criteria
- [ ] Results tab no longer exists in the tab bar.
- [ ] Default tab on detail page is Summary.
- [ ] All existing unit tests pass.
