# PAIML-POLE-ANALYST-041 — AnalysisHistoryService

## Meta
- **Project:** pole_analyst
- **Phase:** 12 — Stitch Design: Tab Navigation + Analysis History
- **Status:** TODO
- **Blocks:** PAIML-POLE-ANALYST-040
- **Blocked By:** PAIML-POLE-ANALYST-038

## Description

Create a service that calls the enriched analysis list endpoint
(`GET /api/analysis/videos/summary`) and provides the data to the AnalysisHistoryTable.

### Tasks
- [ ] Create `AnalysisHistoryService` in `core/services/analysis-history.service.ts`.
- [ ] Implement `list(): Observable<AnalysisSummaryRecord[]>` method.
- [ ] Use `ApiClientService` for HTTP calls.
- [ ] Handle errors (404 → empty list, network errors → error state).
- [ ] Add unit tests with mock `ApiClientService`.

### Acceptance Criteria
- [ ] Service fetches from `GET /api/analysis/videos/summary`.
- [ ] Returns `Observable<AnalysisSummaryRecord[]>`.
- [ ] Error handling returns empty list or error state.
- [ ] Unit tests pass.
