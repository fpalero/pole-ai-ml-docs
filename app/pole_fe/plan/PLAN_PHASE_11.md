# Fase 11 — Class stats histograms + video selection — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md) · Feature: detección automática de fases (handspring) — FE `pole_fe`

## Contexto

La detección automática de fases necesita **histogramas de referencia** por clase. En `pole_fe`
(entrenador/analista) el usuario debe poder:
1. Seleccionar qué videos de una clase (ej. `handspring`) se usan para generar los histogramas de
   referencia.
2. Lanzar la generación y ver el progreso del job.
3. Ver los **histogramas de clase** (stats por métrica) comparados entre sí (curva media del cohort).

Este FE es el productor de la referencia que consumirá `pole_analyst` (detección) y el clasificador.

## Alcance

### 1. Selección de videos + trigger

- Nueva acción en la detail page de tricks: "Generate reference histograms" con selector de videos
  (reutiliza la selección existente de la video grid).
- `POST /api/tools/histograms/references` con `{trick_label, video_ids}` → 202 `{job_id}` → poll
  `GET /api/tools/jobs/{job_id}` (reutiliza `jobs-store`).

### 2. Vista de stats de clase (histogramas)

- Nuevo panel/section en la detail page: "Class histogram stats" para la clase seleccionada.
- Muestra, por métrica (las 5 usadas: `angular_speed`, `body_tilt`, `hip_height`, `wrist_stability`,
  `torso_tilt_speed`), la curva media del cohort (`mean` 300-pt con `phase_bounds`) y el estado de
  referencia (generada / vacía).
- `GET /api/tools/histograms/references?trick_label=handspring` → 200 lista de métricas con
  histogramas; **422** si referencia vacía (muestra empty-state + lista de métricas faltantes).

### 3. Manejo de errores

- Referencia vacía → mensaje "no hay histogramas de referencia; genera con videos seleccionados".
- Video sin fases (`phase_frames`) → se reporta en `skipped` del job.

## Endpoints consumidos

| Endpoint | Método | Uso |
| :--- | :--- | :--- |
| `/api/tools/histograms/references` | POST | Generar referencias (202 job) |
| `/api/tools/histograms/references?trick_label=` | GET | Listar métricas con histogramas |
| `/api/tools/jobs/{id}` | GET | Poll del job (existente) |
| `GET /api/training/classes/{id}/videos` | GET | Selección de videos (existente) |

## Tickets (candidatos)

- [ ] **PAIML-POLE-FE-009** — Domain/App: DTOs + servicios (`ReferenceHistogramDto`; `generateReferences`,
      `getClassHistogramStats`). Blocked by backend `PLAN_PHASE_2` (referencias).
- [ ] **PAIML-POLE-FE-010** — Presentation: action "Generate reference histograms" + selector de videos + job progress.
- [ ] **PAIML-POLE-FE-011** — Presentation: panel Class histogram stats (curvas por métrica, estado de referencia).
- [ ] **PAIML-POLE-FE-012** — Tests: unit + E2E del flujo de generación/visualización.

## Dependencias

- **Blocked By:** backend `pola_api` fases 1–2 (rename colecciones + referencias).

## Criterios de aceptación

- [ ] El usuario puede seleccionar videos y generar histogramas de referencia (202 + poll).
- [ ] La vista de stats de clase muestra las 5 métricas con curva media del cohort.
- [ ] Referencia vacía → 422 mapeado a empty-state con lista de métricas faltantes.
- [ ] Cobertura ≥ 80% en los módulos nuevos.