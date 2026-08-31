# PAIML-POLE-ANALYST-039 — VideosLibrary tab bar

## Meta
- **Project:** pole_analyst
- **Phase:** 12 — Stitch Design: Tab Navigation + Analysis History
- **Status:** TODO
- **Blocks:** PAIML-POLE-ANALYST-040
- **Blocked By:** PAIML-POLE-ANALYST-038

## Description

Add a tab bar to the `VideosLibraryPage` with tabs matching the Stitch design:
- **Video Library** (active default) — current video grid
- **Training Videos** — placeholder (empty state with "Coming soon" message)

The Stitch design shows `Video Library | Training Videos | Crawler Queue` but the PO confirmed
no crawler concept. We implement Video Library + Training Videos placeholder only.

### Tasks
- [ ] Add `TabBar` component to `VideosLibraryPage` header area.
- [ ] Define tab IDs: `'video-library' | 'training-videos'`.
- [ ] Render `VideoLibraryPane` when `video-library` tab is active.
- [ ] Render placeholder component when `training-videos` tab is active.
- [ ] Default active tab: `video-library`.
- [ ] Add unit tests for tab switching behavior.

### Acceptance Criteria
- [ ] VideosLibrary page shows tab bar with "Video Library" active by default.
- [ ] Clicking "Training Videos" shows a placeholder.
- [ ] Tab bar follows the Stitch visual design (active underline, muted inactive).
- [ ] Unit tests pass.
