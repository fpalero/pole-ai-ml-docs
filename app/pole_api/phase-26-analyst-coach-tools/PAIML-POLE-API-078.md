# Ticket: PAIML-POLE-API-078

## Title
[Application] Analyst chatbot tool `frame_pose` — single-frame pose + coaching breakdown

## Description
Phase 26 (PLAN_PHASE_26.md), tool #5. Complementary to `segment_insight`: analyze ONE precise
frame (by absolute frame number or by second) and return the exact joint angles in degrees (from
`analysis-db.skeleton-landmarks.biomech_features`, back-computed when absent), the metric
z-score snapshot at that frame, the classification, and a coaching explanation. Lets the coach ask
"what exactly is wrong at second 3?" and jump to a `video_segment` block around that frame.

## What to Do (Implementation Steps)
- [ ] `AnalystFacade.frame_pose(video_id, frame=None, second=None)` — validate id + exactly one
      selector; resolve to an absolute frame number (second → `round(second * fps)`) using the
      histogram doc's `fps`/`total_frames` (structured error when fps unknown or frame out of range).
- [ ] Reuse `CoachService.insights_for_frames(video_id, [frame])` for the per-frame insight
      (classification, score_pct, z_score, explanation) — lazy LLM generation already cached on
      the video doc; deterministic backfill fallback.
- [ ] Joint angles: read the frame's `biomech_features` row (or back-compute via
      `compute_frame_features`) — return exact degree values for elbow/knee angles and normalized
      extension/width features, plus the existing body-language labels (reuse the band helpers'
      semantics without duplicating private helpers — add small local qualifiers if needed).
- [ ] Compact payload `{frame, second, phase, joint_angles_deg, metrics: {key: {z_score,
      score_pct, label}}, classification, score_pct, explanation}` + `hint_to_agent` to emit a
      `video_segment` covering `[frame-1, frame+1]`.
- [ ] Register `ToolSpec(name="frame_pose", mode="sync", ...)` in `analyst_chatbot/tools.py`,
      params `{video_id: string (required), frame: integer, second: number}`.
- [ ] Add one line to `ANALYST_SYSTEM_PROMPT` tool list.
- [ ] Tests: facade (frame/second resolution, out-of-range, unknown video), angle qualification,
      insights fallback, tool registration.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Returns exact degree angles + metric snapshot + explanation for the requested frame; frame
      and second selectors are interchangeable.
- [ ] Never raises to the WS; structured errors for invalid/ambiguous selectors.
- [ ] `pixi run test-api` green; coverage ≥ 80% maintained.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: None
- **Blocked By**: Phase 22 (`CoachService.insights_for_frames`), Phase 20 (`biomech_features`)

## Estimated Effort
- [M]
