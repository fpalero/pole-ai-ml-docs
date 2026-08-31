# Ticket: PAIML-POLE-API-072

## Title
[Application] Metric deltas endpoint — session-over-session comparison + peak flags

## Description
Phase 24 (PLAN_PHASE_24.md). Implements the backend for the Stitch "Metric Distribution Analysis"
cards: `+X% vs last session` deltas and `Peak Performance` badges. Adds
`GET /api/analysis/videos/{video_id}/metric-deltas` comparing the target video's scored histogram
against the latest prior analyzed video.

## What to Do (Implementation Steps)
- [ ] `AnalysisRepository.find_baseline(video)` — latest prior doc with `analyzed=true`,
      preferring same `trick_label`; returns `None` when no comparable history.
- [ ] Pure delta service: per shared metric key compute `{current, previous, delta_pct, improved}`;
      omit keys missing on either side (never fabricate values).
- [ ] Peak flags: metric keys where the current value is the max across all analyzed videos of the
      same trick (single aggregation).
- [ ] Pydantic DTOs in `analysis/schemas.py` (`MetricDeltasOut`, `MetricDelta`, `PeakFlag`);
      route in `analysis/controllers/videos.py`; 409 when video not analyzed, empty metrics list
      when no baseline (not an error — FE hides the card).
- [ ] Integration tests: baseline same-trick / fallback-none / partial overlap / peak flag /
      not-analyzed guard.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Endpoint contract matches PLAN_PHASE_24; empty-baseline case returns 200 with empty lists.
- [ ] No image/landmark payloads leaked into the response — aggregate numbers only.
- [ ] `pixi run test-api` green; coverage ≥ 80% maintained.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-061
- **Blocked By**: None

## Estimated Effort
- [M]
