# Ticket: PAIML-POLE-FE-007

## Title
[Presentation] Biomechanical Signal Analysis view — synchronized signals + temporal annotation

## Description
Implement the new **Synchronized Biomechanical Analysis** panel from the Stitch `fe_pole` screen
(`projects/8550978881667345493`): a synchronized video player + active-signals chart with a
**temporal annotation** strip (Start / Execution / Exit / End frame capture). This is the **post-analysis
review** step (Q2 resolution, `PLAN.md` §3 Phase 9): the panel opens after `Histo` has produced a
histogram. If no histogram exists for the clip (`GET /api/tools/histograms/{video_id}` → `404`), the
panel shows **nothing** (empty state with a "run Histo first" hint) — no live landmark-derived signals,
no new BE endpoint.

Data sources (existing endpoints):
- Video stream: existing `GET /api/video/clips/{clip_id}/video` (or `/videos/{id}/video`).
- Active signals: `GET /api/tools/histograms/{video_id}` → `metrics` + `resampled` 300-pt curves
  (rendered **only** when a histogram doc exists).
- Phase annotation write: `PUT /api/training/clips/{video_id}/phase-frames`.

## What to Do (Implementation Steps)
- [ ] Add a `biomech-signal-analysis` component (standalone, under
      `features/tricks/components/`) with: video player (reuse the editor player controls pattern),
      a multi-signal chart of the 8 histogram metrics (`horizontal_speed`, `vertical_speed`,
      `angular_speed`, `torso_tilt_speed`, `wrist_stability`, `hip_height`, `body_tilt`,
      `smoothness` — the design's "Vertical Velocity / Angular Momentum / …" labels are illustrative
      placeholders), and metric readouts for the current playhead frame.
- [ ] Load `GET /api/tools/histograms/{video_id}` on open; **`404` → render the empty state and show
      nothing else** (no chart, no annotation strip). Only with a 200 do the chart + annotation render.
- [ ] Add the temporal annotation strip: four capture buttons (Start / Execution / Exit / End) that
      snap the current frame into `ENTRANCE/EXECUTION/EXIT` [start,end] boundaries (Start→ENTRANCE.start,
      Execution→ENTRANCE.end+EXECUTION.start, Exit→EXECUTION.end+EXIT.start, End→EXIT.end) and
      `PUT /api/training/clips/{video_id}/phase-frames`.
- [ ] Open the panel from the clip card (`Edit` action) or a new `Biomech`/"Analyze" affordance;
      handle loading / empty (`404` histogram) / error states.
- [ ] Use a lightweight chart approach consistent with existing deps (e.g. `ng2-charts` if already
      present, else a canvas/SVG series) — do not add a new heavy chart lib without review.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Panel renders a synchronized video + 8-signal chart; playhead drives the metric readouts.
- [ ] Capturing the four annotation points issues `PUT /api/training/clips/{video_id}/phase-frames`
      with the correct `ENTRANCE`/`EXECUTION`/`EXIT` bounds; success/failure feedback shown.
- [ ] Empty/error/loading states covered; no subscription leaks (destroy cleanup).
- [ ] Unit tests for the phase-boundary mapping (4 buttons → 3 phases) and component states.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`.

## Dependencies
- **Blocks**: `PAIML-POLE-FE-008`.
- **Blocked By**: `PAIML-POLE-FE-005`.

## Estimated Effort
- [L]
