# Ticket: PAIML-POLE-ANALYST-032

## Title
[Presentation] ResultsView (timeline de fases, feedback, error frames)

## Description
Phase 9 (§3). After `done`, the athlete sees the analysis result: detected phase timeline
(ENTRADA → EJECUCIÓN → SALIDA) over the video timeline, execution feedback (5 metrics with score
0-100 + deviation vs cohort), and error frame images (one per point `|z| > 1`, with metric/phase
label). Replaces/supplements the Summary/Histogram tabs of Phase 4.

## What to Do (Implementation Steps)
- [ ] ResultsView component: phase timeline over the video timeline.
- [ ] Feedback section: 5 metrics with score + `z_mean` deviation + textual feedback.
- [ ] Error frames gallery from `detections[].frame_image_path` with metric/phase label.
- [ ] Unit tests: rendering with data and empty cases.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] After `done`, phase timeline + feedback + error frames render correctly.
- [ ] `npx ng test --watch=false` green on new modules.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-034
- **Blocked By**: PAIML-POLE-ANALYST-031, PAIML-POLE-ANALYST-030

## Estimated Effort
- [M]