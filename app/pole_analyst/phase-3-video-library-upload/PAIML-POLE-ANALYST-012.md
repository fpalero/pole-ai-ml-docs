# Ticket: PAIML-POLE-ANALYST-012

## Title
[Presentation] VideosLibraryPane (search + video grid + upload dropzone)

## Description
Build the right-pane default mode "My Videos": a search bar, a `VideoCard` grid (thumbnail,
filename, date, "Analyzed"/"Not analyzed" badge, "Analyze"/"Open analysis" action), and the
`UploadDropzone` at the top.

## What to Do (Implementation Steps)
- [ ] Implement `VideosLibraryPane` layout (upload zone + search + grid).
- [ ] Implement `VideoCard` (thumbnail, filename, date, badge, contextual action).
- [ ] Wire search filtering client-side.
- [ ] Wire "Analyze" → trigger analysis (Phase 4) and "Open analysis" → open detail tabs.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] Cards render both badge states and the correct action button.

## Integration Tests to Run (Local Verification)
- [ ] UC-01 (card "Not analyzed"), UC-07 (empty state), UC-02 (Analyze → detail).

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-013, PAIML-POLE-ANALYST-014, PAIML-POLE-ANALYST-021
- **Blocked By**: PAIML-POLE-ANALYST-003, PAIML-POLE-ANALYST-010, PAIML-POLE-ANALYST-011

## Estimated Effort
- [M]
