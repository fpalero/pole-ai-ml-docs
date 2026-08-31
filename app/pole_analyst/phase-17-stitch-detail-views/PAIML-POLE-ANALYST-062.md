# Ticket: PAIML-POLE-ANALYST-062

## Title
[Features] Detail-page parity pass vs Stitch "Analysis Details" screen

## Description
Phase 17 Phase C (PLAN_PHASE_17.md). Closes the remaining visual/interaction gaps between the
analysis detail page and the Stitch *Analysis Details – Fully Interactive Technical Views* screen:
header Overall Score card, correction-drill CTA from insights to Plan drills, PlanTab
objectives/drills layout, `Histogram`→`Statistics` tab label, and Pose Insights list styling.

## What to Do (Implementation Steps)
- [ ] Header Overall Score card (score/100) reusing `summary.ts::pickOverallScore`; hidden when
      not analyzed.
- [ ] Insights warning cards: add `View Correction Drill` CTA that navigates to the Plan tab and
      scrolls to the matching drill/objective (anchor ids on drill cards).
- [ ] PlanTab layout per screen: numbered Core Objectives block + Recommended Drills grid; mapper
      tolerates coach-plan JSON variants (`weeks[]` grouped as objectives when objectives key absent).
- [ ] Rename tab label `Histogram` → `Statistics` in TabBar config; update affected specs/E2E
      selectors.
- [ ] PoseTab insights lists styled as "What's Correct" / "Needs Adjustment" groups per screen.
- [ ] Sidebar per PO decision (2026-08-23): ADD `Coach` nav item pointing to the chat pane
      (reuse the existing chat primary-outlet route, same as `dashboard`); REMOVE the `Settings`
      nav item entirely.
- [ ] Unit specs per change; update Playwright flows touching renamed labels.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Side-by-side review against the Stitch screen shows parity for the listed elements.
- [ ] All existing specs green after label rename.
- [ ] No subscription leaks; lint/typecheck green.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-analyst`
- [ ] Playwright suite (pole_analyst)

## Dependencies
- **Blocks**: none
- **Blocked By**: none (coach tabs Phase 16 merged via #110/#111)

## Estimated Effort
- [M]
