# PAIML-POLE-ANALYST-045 — Consolidate results-summary.ts into summary.ts

## Meta
- **Project:** pole_analyst
- **Phase:** 13 — Stitch Design: Results→Summary merge + Tab Reorder
- **Status:** TODO
- **Blocks:** — (none)
- **Blocked By:** PAIML-POLE-ANALYST-044

## Description

Consolidate the `results-summary.ts` model file into `summary.ts`. The `AnalysisSummaryDto`
and `analysisSummaryDtoFrom()` mapper in `results-summary.ts` produce the same data that
`summary.ts` (`SummaryView`, `summaryViewFromDto()`) consumes. After the Results tab is removed,
the `results-summary.ts` file can be merged into `summary.ts` or removed if no longer needed.

### Tasks
- [ ] Identify which exports from `results-summary.ts` are still used after Results removal.
- [ ] Move any needed mappers/types into `summary.ts`.
- [ ] Remove `results-summary.ts` if no longer needed.
- [ ] Update all imports that reference `results-summary.ts`.
- [ ] Update unit tests.

### Acceptance Criteria
- [ ] `results-summary.ts` is removed or consolidated.
- [ ] All imports are updated.
- [ ] Unit tests pass.
