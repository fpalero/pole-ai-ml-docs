# Ticket: PAIML-CREW-007

## Title
Fix `detect_project` to recognize `docs/packages/`

## Description
`crew_implement.detect_project()` only recognizes `app` and `package` path segments, so it cannot infer the project for tickets stored under `docs/packages/<project>/...` (the plural `packages` segment used for all package docs, e.g. `docs/packages/pole_ml/` and the new `docs/packages/crew/`). This makes `load_tickets()` raise `cannot infer project from path` and stops the crew engine (including `crew-validate`) from loading any package ticket.

## What to Do
- Edit `crew/crew_implement.py` `detect_project(path: Path) -> str`:
  - Change the segment check to recognize both `package` (singular) **and** `packages` (plural), alongside the existing `app` segment.
  - Keep returning the project name as the path segment immediately following the matched container segment.
  - Update the docstring to mention `app`, `package`, and `packages`.
- Verify that `crew-validate docs/packages/pole_ml/phase-8-cli-integration-gapfill` now loads the ticket.
- Verify that `crew-validate docs/packages/crew/phase-1-guardrails` now loads all 6 crew tickets (PAIML-CREW-001..006) and reports a consistent dependency graph.
- Ensure no regression: `crew-validate` on an `docs/app/<project>/...` folder still works.

## Acceptance Criteria
- [ ] `detect_project()` recognizes `app`, `package`, and `packages` segments
- [ ] `pixi run crew-validate docs/packages/pole_ml/phase-8-cli-integration-gapfill` loads the ticket
- [ ] `pixi run crew-validate docs/packages/crew/phase-1-guardrails` loads all 6 tickets and passes (consistent graph)
- [ ] No regression for `docs/app/<project>/...` folders

## Dependencies
- **Blocked By**: None
- **Blocks**: PAIML-CREW-001, PAIML-CREW-002, PAIML-CREW-003, PAIML-CREW-004, PAIML-CREW-005, PAIML-CREW-008
