# Ticket: PAIML-POLE-API-077

## Title
[Application] Analyst chatbot tool `metric_deep_dive` — one metric curve + cohort band + worst frames

## Description
Phase 26 (PLAN_PHASE_26.md), tool #4. The `histogram` tool returns a compressed summary; this sync
tool zooms into ONE metric to answer "why is my <metric> off at second 3?". Returns the metric's
`resampled` curve, the cohort mean/std band (from `skeleton_cohort_signals`), the phase bounds, and
the worst frames per phase for that metric (from `detections` + recomputed z-scores).

## What to Do (Implementation Steps)
- [ ] `AnalystFacade.metric_deep_dive(video_id, metric)` — validate id + metric key; read the
      video's histogram doc (`video_histograms`); fail structured when the metric is absent from
      `resampled`/`z_mean`.
- [ ] Pull the cohort reference for `(trick_label, metric)` via the existing cohort repo
      (`_get_cohort_repo`, `skeleton_cohort_signals`) — reuse `compute_metric_z_score` +
      `detection_phase`/`detection_frame` (as `CoachService._gather_insights` does) to rebuild the
      per-index z-curve from `resampled`.
- [ ] Worst frames: from the stored `detections` filtered to the metric (keep the top-N by
      |z|, e.g. 5) and/or the recomputed z-curve peak indices; include frame number, phase,
      second (via histogram `fps`/`total_frames`), z_score and score_pct.
- [ ] Cap the returned curve (downsample/limit points) so the LLM payload stays small; include
      `phase_bounds` and per-phase worst index so the agent can emit a `video_segment` block.
- [ ] Register `ToolSpec(name="metric_deep_dive", mode="sync", ...)` in `analyst_chatbot/tools.py`,
      params `{video_id: string (required), metric: string (required)}`.
- [ ] Add one line to `ANALYST_SYSTEM_PROMPT` tool list.
- [ ] Tests: facade (known/unknown metric, missing cohort, not-analyzed), z-curve recomputation,
      worst-frame ranking, tool registration.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Returns curve + cohort band + worst frames for exactly one metric; unknown metric → structured
      error listing available metrics.
- [ ] Never raises to the WS; payload capped for the LLM.
- [ ] `pixi run test-api` green; coverage ≥ 80% maintained.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: None
- **Blocked By**: None (reuses `compute_metric_z_score`, `detection_*` from Phase 22)

## Estimated Effort
- [M]
