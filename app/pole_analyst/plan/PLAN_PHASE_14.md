# Fase 14 — Pose Gallery + Metric Detail Modal — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md) · Feature: Stitch "Pole AI Coach" design refresh — FE `pole_analyst`

## Contexto

The Stitch design shows two advanced views that the current codebase does not implement:

1. **Pose Gallery** — a scrollable list of pose thumbnail cards (each with skeleton overlay),
   with one selected card expanding to show the full annotated frame + insights panel
   (What's Correct / Needs Adjustment / How to Improve).

2. **Metric Detail Modal** — clicking a metric card in the Histogram tab opens a modal with
   a full-size chart of that metric's distribution.

Both are read-only enhancements of existing data. No new backend endpoints are needed beyond
Fase 20's `GET /api/analysis/videos/{video_id}/pose/frames`.

## Alcance

### 1. Pose Gallery (replaces current single-frame PoseTab)

Replace the current `PoseTab` (single frame + fallback) with a gallery layout:
- **Left sidebar:** scrollable list of pose thumbnail cards (12x12 thumbnail + phase badge).
- **Right content:** selected frame's full annotated image (skeleton overlay) + insights panel.
- **Insights panel:** three columns — "What's Correct" (green), "Needs Adjustment" (amber),
  "How to Improve" (info). Populated from the frame's `issues[]` and phase data.
- **Legend:** Optimal (green dot) + Correction (red dot) at bottom.

**Backend dependency:** `GET /api/analysis/videos/{video_id}/pose/frames` (PAIML-POLE-API-057, Fase 20 BE).

**Fallback:** When the new endpoint is unavailable (404), degrade gracefully to the existing
single-frame `GET /api/analysis/videos/{video_id}/pose` (current behavior).

### 2. Metric Detail Modal

Add a clickable overlay to the `HistogramTab` metric cards:
- Click a metric card → open a `MetricDetailModal` component.
- Modal shows: metric name, full-size SVG chart (reuse `MetricChart` shared component),
  legend, close button (X + click-outside + Escape).
- Modal is a CDK overlay (Angular CDK `OverlayModule`) or a simple `<dialog>` element.

## Endpoints consumidos

| Endpoint | Metodo | Uso |
| :--- | :--- | :--- |
| `GET /api/analysis/videos/{video_id}/pose/frames` | GET | **Nuevo** (Fase 20 BE) — multi-frame gallery |
| `GET /api/analysis/videos/{video_id}/pose` | GET | Existente — single-frame fallback |
| `GET /api/analysis/videos/{video_id}/histogram` | GET | Existente — metric data for modal |

## Tickets (candidatos)

- [ ] **PAIML-POLE-ANALYST-046** — App/Domain: DTOs for multi-frame pose response.
- [ ] **PAIML-POLE-ANALYST-047** — Presentation: PoseGallery component (thumbnail list + selected frame + insights).
- [ ] **PAIML-POLE-ANALYST-048** — Presentation: replace PoseTab content with PoseGallery.
- [ ] **PAIML-POLE-ANALYST-049** — Presentation: MetricDetailModal component.
- [ ] **PAIML-POLE-ANALYST-050** — Presentation: wire MetricDetailModal click handlers in HistogramTab.
- [ ] **PAIML-POLE-ANALYST-051** — Infrastructure: PoseGalleryService (calls multi-frame endpoint with fallback).

## Dependencias

- **Blocked By:** Fase 12 (tab navigation), Fase 20 backend (multi-frame pose endpoint).

## Criterios de aceptacion

- [ ] PoseTab shows a gallery of thumbnail cards when multiple detections exist.
- [ ] Clicking a thumbnail card shows the full annotated frame + insights.
- [ ] When only one detection exists, the gallery degrades to the single-frame view.
- [ ] Clicking a metric card in HistogramTab opens the MetricDetailModal with full chart.
- [ ] Modal closes on X, click-outside, and Escape key.
- [ ] Cobertura >= 80%.
