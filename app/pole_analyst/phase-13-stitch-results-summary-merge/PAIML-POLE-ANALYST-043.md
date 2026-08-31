# PAIML-POLE-ANALYST-043 — Merge ResultsView into SummaryTab

## Meta
- **Project:** pole_analyst
- **Phase:** 13 — Stitch Design: Results→Summary merge + Tab Reorder
- **Status:** TODO
- **Blocks:** PAIML-POLE-ANALYST-044
- **Blocked By:** PAIML-POLE-ANALYST-038

## Description

Merge the ResultsView's unique elements into the SummaryTab. The ResultsView currently shows:
- Phase timeline (proportional bar with Entry/Hold/Exit legend)
- Per-metric feedback (score/100, signed z, text feedback)
- Error frames gallery (detections with `frame_image_path`)

The SummaryTab currently shows:
- Phase deviation counts (Entry/Hold/Exit)
- Critical frame/chips
- Max z-score
- Assessment paragraph

Both are fed by `GET /api/analysis/videos/{id}/summary`.

### Tasks
- [ ] Add phase timeline component to the top of SummaryTab.
- [ ] Add error frames gallery to the bottom of SummaryTab.
- [ ] Keep existing metric cards, critical chips, max z-score, assessment.
- [ ] Ensure the merged view renders correctly with all data.
- [ ] Update SummaryTab unit tests to cover new elements.

### Acceptance Criteria
- [ ] SummaryTab shows phase timeline + metric cards + error frames + assessment.
- [ ] All data comes from the same `/summary` endpoint.
- [ ] Unit tests pass.
