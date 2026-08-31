# PAIML-POLE-ANALYST-047 — PoseGallery component

## Meta
- **Project:** pole_analyst
- **Phase:** 14 — Stitch Design: Pose Gallery + Metric Detail Modal
- **Status:** TODO
- **Blocks:** PAIML-POLE-ANALYST-048
- **Blocked By:** PAIML-POLE-ANALYST-046

## Description

Build the `PoseGalleryComponent` that replaces the current single-frame PoseTab layout.
The Stitch design shows:
- Left sidebar: scrollable list of pose thumbnail cards (12x12 thumbnail + phase badge).
- Right content: selected frame's full annotated image (skeleton overlay) + insights panel.
- Insights panel: three columns — "What's Correct" (green), "Needs Adjustment" (amber),
  "How to Improve" (info).
- Legend: Optimal (green dot) + Correction (red dot) at bottom.

### Tasks
- [ ] Create `PoseGalleryComponent` in `features/analysis/components/pose-gallery/`.
- [ ] Implement thumbnail list sidebar (scrollable, selectable cards).
- [ ] Implement selected frame display (annotated image via `AnnotatedFrame`).
- [ ] Implement insights panel (3 columns: correct/adjustment/improve).
- [ ] Implement legend component.
- [ ] Handle loading/empty/error states.
- [ ] Add unit tests.

### Acceptance Criteria
- [ ] Gallery shows thumbnail cards when multiple detections exist.
- [ ] Clicking a thumbnail shows the full annotated frame + insights.
- [ ] Insights are populated from the frame's issues and phase data.
- [ ] Unit tests pass.
