# Fase 11 — Histogram Analysis endpoints — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md)

## Contexto

Histogram analysis refactor: se eliminan `POST /api/tools/analyze`, `/api/tools/reference/*`,
`/api/tools/attempts/*` y se sustituyen por `POST /api/tools/histograms/analysis`,
`GET /api/tools/histograms/{video_id}`, `GET /api/tools/histograms/summary/{video_id}`.

## Alcance detallado

- **Feature Context:** `pole_fe` necesita consultar análisis de histogramas por video. Los endpoints
  actuales (`POST /api/tools/analyze`, `/api/tools/reference/*`, `/api/tools/attempts/*`) serán
  reemplazados por un único modelo: análisis on-demand que produce `skeleton_histograms` +
  `signal_histograms` (o reusa los existentes).
- **Componente(s):** `app/pola_api/api/tools` (router + service), `tools_histograms` collection.
- **Dependencias:** histogram pipeline (Fase 9), models de métricas.

### Endpoints

- `POST /api/tools/histograms/analysis` — análisis de un video (body `{video_id}`); produce/reusa
  `skeleton_histograms` y actualiza `signal_histograms` (cohort stats). 202 job o 200 directo.
- `GET /api/tools/histograms/{video_id}` — retorna el doc `skeleton_histograms` del video (o 404).
- `GET /api/tools/histograms/summary/{video_id}` — resumen (z-scores por métrica, detección de
  critical frame/phase/metric).

### Estado

- **PLANNED** (detalle completo en el PLAN.md original §8).

## Dependencias

- Fase 9 (pipeline de histogramas).

## Criterios de aceptación

- 3 endpoints funcionales; endpoints legacy `/analyze`, `/reference/*`, `/attempts/*` retirados;
  FE no roto (no consumía estos REST aún).