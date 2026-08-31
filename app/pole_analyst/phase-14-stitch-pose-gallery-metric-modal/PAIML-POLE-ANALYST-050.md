# PAIML-POLE-ANALYST-050 — Wire MetricDetailModal in HistogramTab

## Meta
- **Project:** pole_analyst
- **Phase:** 14 — Stitch Design: Pose Gallery + Metric Detail Modal
- **Status:** TODO
- **Blocks:** — (none)
- **Blocked By:** PAIML-POLE-ANALYST-049

## Description

Add click handlers to the HistogramTab metric cards that open the MetricDetailModal
with the selected metric's data.

### Tasks
- [ ] Add `(click)` handler to each metric card in `HistogramTab`.
- [ ] Track selected metric state (metric name + data).
- [ ] Render `MetricDetailModalComponent` when a metric is selected.
- [ ] Pass metric data (resampled curve, z_mean, score) to the modal.
- [ ] Add unit tests for click-to-open behavior.

### Acceptance Criteria
- [ ] Clicking a metric card opens the modal with that metric's chart.
- [ ] Modal receives the correct data.
- [ ] Unit tests pass.
