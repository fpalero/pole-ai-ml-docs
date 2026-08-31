# Fase 16 — Reference histograms (tools) — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md) · Feature: detección automática de fases (handspring) — backend

## Contexto

Generar y exponer los **histogramas de referencia** por truco (`skeleton_trick_histograms`) a partir
de clips aprobados, y servir los datos de histogramas para el FE de `pole_fe` (class stats
histograms + video selection).

## Alcance

### 1. Generación de referencias (slice `tools`)

- Extender `HistogramDataProcessor` / `HistogramAnalysisService` con
  **`upsert_trick_histograms`** (reutilizar resample + binning existentes).
- CLI / endpoint: `POST /api/tools/histograms/references` (o task `pole_tools`) que agrega
  histogramas de referencia por `(trick_label, metric, phase)` desde los clips
  `approved`/`accepted` de cada truco.
- Update `source_count` al regenerar; `last_updated` timestamp.

### 2. Endpoints de referencia para FE

- `GET /api/tools/histograms/references/{trick_label}` — histogramas de referencia del truco
  (por métrica y fase).
- `GET /api/tools/histograms/classes` — trucos con histogramas de referencia disponibles
  (para la selección de video en `pole_fe` Phase 11).

### 3. Métricas (5 usadas)

`angular_speed` (0.40), `body_tilt` (0.25), `hip_height` (0.15), `wrist_stability` (0.15),
`torso_tilt_speed` (0.05). Descartadas: `horizontal_speed`, `vertical_speed`, `smoothness`.

- Bins configurable por métrica (default `[-3.0, -2.5, ..., 1.0]`, 8 bins).

## Tickets (candidatos)

- [ ] **PAIML-POLE-API-043** — `upsert_trick_histograms` + CLI/task de generación de referencias.
- [ ] **PAIML-POLE-API-044** — Endpoints `GET /api/tools/histograms/references/{trick_label}` y
      `/classes`.
- [ ] **PAIML-POLE-API-045** — Regeneración + reseed de referencias para los trucos existentes.

## Dependencias

- Fase 15 (colección `skeleton_trick_histograms`).
- Reutiliza: `HistogramAnalysisService`, `HistogramDataProcessor` (`packages/pole-train-model`).

## Criterios de aceptación

- Referencias por truco generadas y consultables.
- FE `pole_fe` consume los endpoints de referencia.