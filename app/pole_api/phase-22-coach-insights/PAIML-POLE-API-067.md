# Ticket: PAIML-POLE-API-067

## Title
[Application] CoachInsightsService — threshold-based frame classification + persistence

## Description
Phase 22 (§3). Create `analysis/services/coach_insights_service.py`: a rule-based service that
reads detections from `video_histograms`, classifies each frame using z-score thresholds, and
stores structured insights in a new `coach_insights` collection.

**Thresholds:**
- `|z| <= 0.5` → **perfect** (green ✅)
- `0.5 < |z| <= 2` → **adjustment** (yellow ⚠️)
- `|z| > 2` → **wrong** (red ❌)

Each insight includes: metric name, phase, frame number, z-score, classification, and a
human-readable explanation generated from templates (no LLM).

**Metrics (5 REFERENCE_METRICS):** angular_speed (0.40), body_tilt (0.25), hip_height (0.15),
wrist_stability (0.15), torso_tilt_speed (0.05).

## What to Do (Implementation Steps)
- [ ] Create `CoachInsightsService` with injectable deps: `histogram_repo`, `video_repo`.
- [ ] `compute(video_id) -> CoachInsightsResult`:
  - Read `video_histograms` detections for the video.
  - For each detection, compute per-metric z-scores (reuse `compute_metric_z_score`).
  - Classify each frame-metric pair using thresholds.
  - Generate human-readable explanation per insight from templates.
  - Return structured result with perfect/adjustment/wrong lists.
- [ ] `get(video_id) -> CoachInsightsResult | None`: read from `coach_insights` collection.
- [ ] `ensure(video_id) -> CoachInsightsResult`: get-or-compute (Q5C).
- [ ] `persist(video_id, result)`: upsert into `coach_insights` collection.
- [ ] Add `coach_insights` collection schema (Pydantic model for stored doc).
- [ ] Explanation templates: `{metric} in {phase} phase at frame {frame} shows {status}: {detail}`.
- [ ] Unit tests: mock repos, verify classification, verify persistence, verify get-or-compute.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `compute()` correctly classifies frames using thresholds.
- [ ] `get()` returns stored insights or `None`.
- [ ] `ensure()` computes when missing, returns cached when present.
- [ ] Explanations are human-readable and grounded in actual values.
- [ ] Unit tests pass for all methods.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-068, PAIML-POLE-API-069
- **Blocked By**: None (reads from existing `video_histograms`)

## Estimated Effort
- [M]
