# Fase 9 — Extraction → Process (biometric + histogram) flow — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md)

## Contexto

> **Fuente:** Stitch `fe_pole` ("Pole AI Workflow Manager", `projects/8550978881667345493`), update
> 2026-08-13. Screens analizados: **Synchronized Biomechanical Analysis** (nuevo), **Tricks Registry —
> Crop Review & Validation Modal**, **Training Studio**, **Model Registry — Pole AI**, **System Jobs
> Dashboard**. La toolbar del workflow gana pasos `Extract` / `Biomech` / `Histo`, la filter bar de
> clips gana estados `EXTRACTED` / `HISTO`, y un nuevo panel **Biomechanical Signal Analysis** añade
> un video sincronizado + chart de señales activas con **annotación temporal** (Start / Execution /
> Exit / End frame capture).
>
> **Clasificación: FE + BE integration (pequeña extensión BE).** Los endpoints del flujo ya existen;
> el único cambio backend es el soporte del estado `HISTO` (PO 2026-08-13): `pola_api` **Phase 14**
> (`docs/app/pola_api/PLAN.md` §10) marca `videos.histogram_processed=true` en ambas rutas productoras
> de histograma y añade conteos clip-scoped `extracted`/`histo` (`X-Count-*`). Tickets
> `PAIML-POLA-API-036..038`; FE consume el flag + counts — **sin N+1** y sin nuevo endpoint de histograma.

| Design element | Endpoint / contract | Provider |
| :--- | :--- | :--- |
| Extract action + `EXTRACTED` status | `POST /api/training/classes/{id}/extract`; `extracted` flag en `GET /api/training/classes/{id}/videos` | existing |
| Biomech action (biometric windows) | `POST /api/training/classes/{id}/process` → `BiomechanicalDataProcessor` → `skeleton_windows` | existing |
| Histo action (histogram + summary) | `POST /api/tools/histograms/analysis`; `GET /api/tools/histograms/{video_id}`; `GET /api/tools/histograms/summary/{video_id}` | existing |
| `HISTO` status + filter counts | `videos.histogram_processed` flag + `X-Count-extracted`/`X-Count-histo` | **new BE Phase 14** (`PAIML-POLA-API-036..038`) |
| Temporal annotation (phase frames) | `PUT /api/training/clips/{video_id}/phase-frames` (`ENTRANCE`/`EXECUTION`/`EXIT` [start,end]) | existing |
| Active-signals chart (post-analysis) | `GET /api/tools/histograms/{video_id}` (`metrics` + `resampled` 300-pt curves) | existing |

## Tickets (candidatos)

- [ ] **PAIML-POLE-FE-005** — Domain/App: pipeline DTOs + service wiring (`extracted`/`phase_frames`/
      `landmarks`/`histogram_processed` en `VideoRecordDto`; `HistogramDto`/`HistogramSummaryDto`;
      `extract`, `setPhaseFrames`, `submitHistogramAnalysis`, `getHistogram`, `getHistogramSummary`).
      Blocked by `PAIML-POLA-API-036`.
- [ ] **PAIML-POLE-FE-006** — Presentation: `Extract`/`Biomech`/`Histo` bulk actions +
      `EXTRACTED`/`HISTO` filter statuses (trick-detail toolbar + pills, counts desde `X-Count-*`).
      Blocked by `PAIML-POLA-API-037`.
- [ ] **PAIML-POLE-FE-007** — Presentation: Biomechanical Signal Analysis view (video sincronizado +
      active-signals chart + annotación temporal → `PUT /api/training/clips/{id}/phase-frames`).
      **Post-analysis only** (Q2 resolution).
- [ ] **PAIML-POLE-FE-008** — Tests: unit + Playwright E2E para el flujo extraction → process
      (biometric + histogram).

## Decisiones resueltas (PO 2026-08-13)

- **Q1 — `HISTO` status source:** ✅ **RESOLVED → add flag + count.** `pola_api` Phase 14
  (`PAIML-POLA-API-036..038`) marca `videos.histogram_processed=true` en cada producción de histograma
  exitosa y extiende `count_by_status`/`list_videos` con counts clip-scoped `extracted`/`histo`.
  FE lee el flag de los docs de video y los counts de `X-Count-*` — sin N+1 por clip.
- **Q2 — active-signals data source:** ✅ **RESOLVED → post-analysis only.** El panel Biomechanical
  Signal Analysis renderiza tras `Histo` haber producido un histograma; si `GET /api/tools/histograms/{video_id}`
  devuelve `404` (sin histograma), el panel muestra **nada** (empty state) — sin señales derivadas de
  landmarks en vivo, sin nuevo endpoint BE.