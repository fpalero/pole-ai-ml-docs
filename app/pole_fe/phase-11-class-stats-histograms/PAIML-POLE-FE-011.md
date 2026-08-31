# Ticket: PAIML-POLE-FE-011

## Title
[Presentation] Panel Class histogram stats (curvas por métrica, estado de referencia)

## Description
Phase 11 (§2). New panel/section on the trick detail page: "Class histogram stats". For the selected
class, shows per metric (the 5 used: `angular_speed`, `body_tilt`, `hip_height`, `wrist_stability`,
`torso_tilt_speed`) the cohort mean curve (`mean` 300-pt with `phase_bounds`) and the reference state
(generated / empty). Empty reference → 422 → empty-state with list of missing metrics.

## What to Do (Implementation Steps)
- [ ] "Class histogram stats" panel on trick detail for the selected class.
- [ ] Per metric: cohort mean curve (300-pt, phase_bounds) + reference state.
- [ ] Empty reference → empty-state message "no hay histogramas de referencia; genera con videos seleccionados" + missing metrics.
- [ ] Unit tests: rendering with data and empty-state.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Panel shows the 5 metrics with cohort mean curves.
- [ ] Empty reference maps to empty-state with missing metrics.
- [ ] `npx ng test --watch=false` green on new modules.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`.

## Dependencies
- **Blocks**: PAIML-POLE-FE-012
- **Blocked By**: PAIML-POLE-FE-009, PAIML-POLE-API-044

## Estimated Effort
- [M]