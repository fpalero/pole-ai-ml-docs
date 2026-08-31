# Ticket: PAIML-POLE-ANALYST-018

## Title
[Presentation] PoseTab (annotated frame with skeleton overlay)

## Description
Build the Pose tab: show an annotated frame from the user's video with a skeleton overlay +
correction hints. Read from the pose endpoint (or fall back to
`detections[].frame_image_path` from the histogram doc).

## What to Do (Implementation Steps)
- [ ] Implement `PoseTab` + `AnnotatedFrame` component.
- [ ] Fetch the pose frame (`GET /api/analysis/videos/{id}/pose`, fallback to detections).
- [ ] Render the image with skeleton overlay + issue callouts.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] Pose frame renders (or degrades gracefully if the pose model is unavailable).

## Integration Tests to Run (Local Verification)
- [ ] UC-03: Pose tab shows the annotated frame for an analyzed video.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-020
- **Blocked By**: PAIML-POLE-ANALYST-003, PAIML-POLE-ANALYST-015

## Estimated Effort
- [M]
