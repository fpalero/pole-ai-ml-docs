# Ticket: PAIML-POLE-ANALYST-001

## Title
[Infrastructure] Angular 22 scaffold + design tokens + two-pane split shell

## Description
Bootstrap the new `app/pole_analyst` Angular SPA ("Pole AI Coach"). Reuse the `pole_fe`
conventions (Angular 22 esbuild, Tailwind, `@angular/build:unit-test` vitest runner). Establish
the light-theme design tokens from `docs/app/pole_analyst/fe_design.md` and the two-pane shell
(slim top bar + 40%/60% chat/tools split).

## What to Do (Implementation Steps)
- [ ] Scaffold `app/pole_analyst` with Angular 22 (esbuild) + Tailwind + vitest unit runner.
- [ ] Add design tokens (colors, typography, spacing) from `fe_design.md` to a tokens/theme module.
- [ ] Build the shell layout: slim top bar (logo + subtitle + avatar/settings) and the two-pane
      split (left chat ~40%, right tools ~60%) with independent scrolling and an 8px grid.
- [ ] Wire lazy routes for `chat` and `videos`/`analysis` features.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng build` and `ng lint` pass.
- [ ] The shell renders the two-pane layout and top bar per the design.
- [ ] Design tokens are centralized (no hardcoded colors/spacing).
- [ ] Existing repo `pole_fe` tooling conventions are mirrored.

## Integration Tests to Run (Local Verification)
- [ ] UC-07: Empty library — shell renders with right pane ready for the upload panel.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-002, PAIML-POLE-ANALYST-003, PAIML-POLE-ANALYST-004, PAIML-POLE-ANALYST-025, PAIML-POLE-ANALYST-028
- **Blocked By**: —

## Estimated Effort
- [M]
