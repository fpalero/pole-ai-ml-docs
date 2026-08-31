# Fase 13 — Results→Summary merge + Tab Reorder — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md) · Feature: Stitch "Pole AI Coach" design refresh — FE `pole_analyst`

## Contexto

The Stitch design specifies 4 tabs: **Summary | Histogram | Pose | Plan**. The current code
has 5 tabs: Results | Summary | Histogram | Pose | Plan. This phase merges the ResultsView
content into the SummaryTab and removes the standalone Results tab.

The ResultsView currently shows: phase timeline, per-metric feedback, and error frames gallery.
The SummaryTab currently shows: phase deviation counts, critical frame/chips, max z-score, and
assessment paragraph. Both are fed by `GET /api/analysis/videos/{id}/summary`.

## Alcance

### 1. Merge Results content into Summary

Merge the ResultsView's unique elements into the SummaryTab:
- **Phase timeline** (proportional bar with Entry/Hold/Exit legend) — add to top of SummaryTab.
- **Error frames gallery** (detections with `frame_image_path`) — add to bottom of SummaryTab.
- Keep existing SummaryTab content: metric cards, critical chips, max z-score, assessment paragraph.

### 2. Remove Results tab

- Remove `ResultsView` component and its spec.
- Remove `'Results'` from `AnalysisTabId` union type.
- Update `AnalysisDetailPage` to default to `'Summary'` tab instead of `'Results'`.
- Update `TabBar` tabs to: Summary | Histogram | Pose | Plan.

### 3. DTO consolidation

- Merge `results-summary.ts` (`AnalysisSummaryDto`) into `summary.ts` (`SummaryView`).
- The `analysisSummaryDtoFrom()` mapper already produces the data; ensure SummaryTab consumes it.

## Endpoints consumidos

| Endpoint | Metodo | Uso |
| :--- | :--- | :--- |
| `GET /api/analysis/videos/{id}/summary` | GET | Existente — merged view |
| `GET /api/analysis/videos/{id}/histogram` | GET | Existente — fallback for detections |

## Tickets (candidatos)

- [ ] **PAIML-POLE-ANALYST-043** — Presentation: merge ResultsView phase timeline + error frames into SummaryTab.
- [ ] **PAIML-POLE-ANALYST-044** — Presentation: remove Results tab, update AnalysisTabId, set default to Summary.
- [ ] **PAIML-POLE-ANALYST-045** — Domain: consolidate results-summary.ts into summary.ts.

## Dependencias

- **Blocked By:** Fase 12 (tab navigation).

## Criterios de aceptacion

- [ ] Summary tab shows phase timeline + metric cards + error frames + assessment.
- [ ] Results tab no longer exists in the tab bar.
- [ ] Default tab on detail page is Summary.
- [ ] All existing unit tests pass (results-summary models may be removed or consolidated).
- [ ] Cobertura >= 80%.
