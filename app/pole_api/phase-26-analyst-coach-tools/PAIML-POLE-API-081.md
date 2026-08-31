# Ticket: PAIML-POLE-API-081

## Title
[Application] Analyst chatbot tool `risk_scan` — injury-risk frame scanning

## Description
Phase 26 (PLAN_PHASE_26.md), tool #8. Adds a sync `risk_scan` chatbot tool that scans the whole
video for injury-risk moments: joint-angle extremes (knee/elbow hyperextension, deeply bent
landings) derived from `analysis-db.skeleton-landmarks.biomech_features` (back-computed when
absent) and frames where a metric deviates very strongly from the cohort. Reuses the pose-issue
band logic (`pose_service.build_pose_issues`) as the v1 threshold source (PLAN_PHASE_26 open
question — no new tuning in v1).

## What to Do (Implementation Steps)
- [ ] Pure helper `scan_risk_frames(feature_rows, fps, thresholds=None)` — per frame, flag joints
      whose angle crosses a safety band (hyperextension past the straight range, or deep flexion),
      returning `{frame, second, joint, angle_deg, risk_kind, note}`; thresholds default from the
      `build_pose_issues` bands (v1) and are injectable for tests.
- [ ] Optionally enrich each flagged frame with the metric z-scores at that index (reuse the
      z-curve recomputation pattern from `metric_deep_dive`) and the strongest |z| metric.
- [ ] `AnalystFacade.risk_scan(video_id)` — validate id; structured error for no landmarks /
      unanalyzed video; cap the returned flagged frames (top-N by severity, e.g. 10) and include a
      `hint_to_agent` instructing a cautious tone (informational, not a medical diagnosis) and
      `video_segment` blocks per flagged frame.
- [ ] Register `ToolSpec(name="risk_scan", mode="sync", ...)` in `analyst_chatbot/tools.py`,
      params `{video_id: string (required)}`.
- [ ] Add one line to `ANALYST_SYSTEM_PROMPT` tool list.
- [ ] Tests: pure scan (hyperextension / deep-flexion flags, threshold injection, no-flags case),
      facade (no landmarks, caps), tool registration.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Flags are deterministic, bounded (top-N), and reference concrete frames/seconds; no-risk
      videos return an empty flagged list (not an error).
- [ ] Never raises to the WS; structured errors for missing input data.
- [ ] `pixi run test-api` green; coverage ≥ 80% maintained.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: None
- **Blocked By**: Phase 20 (`biomech_features`), Phase 22 (`pose_service.build_pose_issues`)

## Estimated Effort
- [M]
