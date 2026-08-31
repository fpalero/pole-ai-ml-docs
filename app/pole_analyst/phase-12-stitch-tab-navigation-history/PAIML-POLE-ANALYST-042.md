# PAIML-POLE-ANALYST-042 — Router: history route + navigation wiring

## Meta
- **Project:** pole_analyst
- **Phase:** 12 — Stitch Design: Tab Navigation + Analysis History
- **Status:** TODO
- **Blocks:** — (none)
- **Blocked By:** PAIML-POLE-ANALYST-040

## Description

Add the analysis history route to the router and wire navigation from the video library cards.

### Tasks
- [ ] Add route: `'history'` (named outlet `tools`) → `AnalysisHistoryPage` (lazy).
- [ ] Add navigation link from VideosLibraryPage header to history view.
- [ ] Ensure the chat pane remains visible when navigating to history (left outlet unchanged).
- [ ] Update `app.routes.ts` with the new route.
- [ ] Add unit tests for route configuration.

### Acceptance Criteria
- [ ] Navigating to `/chat (tools:history)` shows the Analysis History page.
- [ ] Chat pane remains visible on the left.
- [ ] Navigation from video library to history works.
- [ ] Unit tests pass.
