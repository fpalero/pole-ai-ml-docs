# PAIML-POLE-ANALYST-049 — MetricDetailModal component

## Meta
- **Project:** pole_analyst
- **Phase:** 14 — Stitch Design: Pose Gallery + Metric Detail Modal
- **Status:** TODO
- **Blocks:** PAIML-POLE-ANALYST-050
- **Blocked By:** — (none)

## Description

Build a modal component that shows a full-size histogram chart for a single metric.
The Stitch design shows: clicking a metric card in the HistogramTab opens a modal with
the metric name, full-size SVG chart, legend, and close button.

### Tasks
- [ ] Create `MetricDetailModalComponent` in `features/analysis/components/metric-detail-modal/`.
- [ ] Implement modal overlay (CDK Overlay or `<dialog>` element).
- [ ] Render metric name + full-size `MetricChart` component.
- [ ] Implement close: X button, click-outside, Escape key.
- [ ] Add unit tests for open/close behavior.

### Acceptance Criteria
- [ ] Modal opens with metric name and full-size chart.
- [ ] Modal closes on X, click-outside, and Escape.
- [ ] Unit tests pass.
