# Fase 12 — Stitch Design Integration: Tab Navigation + Analysis History — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md) · Feature: Stitch "Pole AI Coach" design refresh — FE `pole_analyst`

## Contexto

The `pole_analyst` Angular FE is being updated to match the refreshed Stitch "Pole AI Coach"
design. This phase adds the top-level tab navigation to the videos page and builds the Analysis
History table that the Stitch design requires.

**Stitch screens analyzed:** 7 interactive screens fetched from the Stitch project
(`projects/4315784734923719370`): Summary, Dashboard - Video Library, Analysis - Histogram View,
Analysis - Improvement Plan, Analysis - Histogram with Detail Modal, Analysis - History and Detail
View, Analysis - Pose Gallery and Detail View.

**Key decisions (confirmed by PO):**
- Replace `Results` tab with `Summary` (4 tabs: Summary, Histogram, Pose, Plan)
- Build Analysis History table
- Build Pose Gallery (multiple frames)
- Build Metric Detail Modal
- Keep 40/60 split layout
- No crawler concept in the design

## Alcance

### 1. Tab navigation on videos page

Add a `TabBar` to the `VideosLibraryPage` with tabs matching the Stitch design:
- **Video Library** (active default) — current video grid
- **Training Videos** — future (show placeholder/empty state for now)

The Stitch design shows `Video Library | Training Videos | Crawler Queue` but the PO confirmed
no crawler concept. We implement Video Library + Training Videos placeholder only.

### 2. Analysis History table

New component `AnalysisHistoryTable` that displays past analyses in a tabular format:

| Column | Source | Notes |
| :--- | :--- | :--- |
| Video Name | `filename` | With thumbnail preview |
| Date | `created_at` | UTC formatted |
| Trick/Move | `trick_label` | From enriched endpoint |
| Score | `overall_score` | X/100 format |
| Status | `analyzed` | "Analyzed" (green) / "Processing" (gray) |
| Action | — | "Open" button |

**Backend dependency:** `GET /api/analysis/videos/summary` (PAIML-POLE-API-056, Fase 20 backend).

### 3. Router changes

- Add route for history view: `'history'` (named outlet `tools`) → `AnalysisHistoryPage`
- Keep existing `'videos'` and `'videos/:videoId/analysis'` routes
- Default redirect: `''` → `'chat'` (unchanged)

## Endpoints consumidos

| Endpoint | Metodo | Uso |
| :--- | :--- | :--- |
| `GET /api/analysis/videos/summary` | GET | **Nuevo** (Fase 20 BE) — enriched list for history table |
| `GET /api/analysis/videos` | GET | Existente — video library grid |

## Tickets (candidatos)

- [ ] **PAIML-POLE-ANALYST-038** — App/Domain: DTOs for enriched analysis summary list.
- [ ] **PAIML-POLE-ANALYST-039** — Presentation: VideosLibrary tab bar (Video Library + Training Videos placeholder).
- [ ] **PAIML-POLE-ANALYST-040** — Presentation: AnalysisHistoryTable component + AnalysisHistoryPage.
- [ ] **PAIML-POLE-ANALYST-041** — Infrastructure: AnalysisHistoryService (calls enriched endpoint).
- [ ] **PAIML-POLE-ANALYST-042** — Router: add history route + wire navigation from library cards.

## Dependencias

- **Blocked By:** backend `pola_api` Fase 20 (`GET /api/analysis/videos/summary`).

## Criterios de aceptacion

- [ ] VideosLibrary page shows tab bar with "Video Library" active and "Training Videos" placeholder.
- [ ] Analysis History table displays video name, date, trick, score, status from the enriched endpoint.
- [ ] Clicking "Open" on a history row navigates to the detail view.
- [ ] Empty state shows "No analyses yet" with CTA to upload.
- [ ] Cobertura >= 80% en modulos nuevos.
