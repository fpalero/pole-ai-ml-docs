# Ticket: PAIML-POLE-ML-002

## Title
[Tests] Fix analysis-tools metric alias drift after M-01..M-05 refactor (8 failing tests)

## Description
`pole_ml.processors.histogram_processor.METRIC_NAMES` was refactored to a **5-metric set**
(`angular_speed` M-01, `torso_tilt_speed` M-02, `wrist_stability` M-03, `hip_height` M-04,
`body_tilt` M-05) — dropping `horizontal_speed`, `vertical_speed`, and `smoothness`.
`analysis_tools.plot.METRIC_ALIASES` (and its tests) were NOT updated, so they still map the
removed metrics: `"hx" → "horizontal_speed"`, `"vx" → "vertical_speed"`, `"sm" → "smoothness"`.
`resolve_metrics()` therefore raises `ValueError: unknown metric` for `hx`/`vx`/`sm`, and the
export tests still assert the old metric names. Result: `pixi run test-analysis-tools` is RED
(8 failed / 35 passed).

Failing tests (all metric-drift, no logic bug):
- `tests/test_cli_plot.py::test_resolve_metrics_aliases`
- `tests/test_cli_plot.py::test_resolve_metrics_full_names_and_dedup`
- `tests/test_cli_plot.py::test_resolve_metrics_all_aliases_are_valid`
- `tests/test_cli_plot.py::test_main_plots_each_metric`
- `tests/test_cli_plot.py::test_main_skips_metric_without_usable_curves`
- `tests/test_cli_plot.py::test_main_requires_video_ids`
- `tests/test_cli_export_analysis.py::test_build_payload_contains_all_sections`
- `tests/test_cli_export_analysis.py::test_main_writes_json_and_markdown`

## Repository
pole-ai-ml

## Affected
- `packages/analysis-tools/src/analysis_tools/plot.py` (`METRIC_ALIASES`)
- `packages/analysis-tools/tests/test_cli_plot.py`
- `packages/analysis-tools/tests/test_cli_export_analysis.py`

## What to Do (Implementation Steps)
- [ ] Step 1: In `plot.py`, reconcile `METRIC_ALIASES` to the canonical 5-metric set from `pole_ml.processors.histogram_processor.METRIC_NAMES` — remove `hx`/`vx`/`sm` (or remap them only if a valid target exists); keep `ax`→angular_speed, `tx`→torso_tilt_speed, `ws`→wrist_stability, `hh`→hip_height, `bt`→body_tilt
- [ ] Step 2: Update the 8 tests to assert the new metric names/aliases (no `horizontal_speed`/`vertical_speed`/`smoothness`)
- [ ] Step 3: No production behavior change — this is a test/alias alignment, not a metric logic change

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pixi run test-analysis-tools` GREEN (all 43 pass, 0 fail)
- [ ] `METRIC_ALIASES` keys map only to names present in `pole_ml` `METRIC_NAMES`
- [ ] No `horizontal_speed`/`vertical_speed`/`smoothness` string left in analysis-tools tests

## Dependencies
- **Blocks:** None
- **Blocked By:** None
- **Related:** PAIML-POLE-ML-001 (CLI integration gap-fill)