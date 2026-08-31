# PAIML-POLE-ANALYST-040 — AnalysisHistoryTable + AnalysisHistoryPage

## Meta
- **Project:** pole_analyst
- **Phase:** 12 — Stitch Design: Tab Navigation + Analysis History
- **Status:** TODO
- **Blocks:** PAIML-POLE-ANALYST-042
- **Blocked By:** PAIML-POLE-ANALYST-039, PAIML-POLE-ANALYST-041

## Description

Build the Analysis History table component and page. The Stitch design shows a two-column layout:
left chat pane (40%) + right pane (60%) with a table of past analyses.

### Table columns (from Stitch design)
| Column | Source | Notes |
| :--- | :--- | :--- |
| Video Name | `filename` | With thumbnail preview (12x12) |
| Date | `created_at` | UTC formatted ("Oct 24, 2023") |
| Trick/Move | `trick_label` | From enriched endpoint |
| Score | `overall_score` | X/100 format |
| Status | `analyzed` | "Analyzed" (green pill) / "Processing" (gray pill) |
| Action | — | "Open" button (navigates to detail) |

### Tasks
- [ ] Create `AnalysisHistoryTableComponent` in `features/analysis/components/analysis-history-table/`.
- [ ] Create `AnalysisHistoryPage` in `features/analysis/pages/history/`.
- [ ] Implement table with columns matching the Stitch design.
- [ ] Add "Filter" button (placeholder for future filtering).
- [ ] Empty state: "No analyses yet — upload a video to get started".
- [ ] Clicking "Open" navigates to the detail view (`/videos/:id/analysis`).
- [ ] Add unit tests for the table component.

### Acceptance Criteria
- [ ] Table displays video name, date, trick, score, status from the enriched endpoint.
- [ ] "Open" button navigates to the detail view.
- [ ] Empty state shows appropriate message.
- [ ] Unit tests pass.
