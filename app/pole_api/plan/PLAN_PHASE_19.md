# Fase 19 — Error contracts + reprocessing + quality gates — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md) · Feature: detección automática de fases (handspring) — backend

## Contexto

Consolidar los contratos de error y reprocesamiento del nuevo pipeline de análisis (upload →
extraction → processing → phase detection → classification → feedback) y cerrar los quality gates
del feature.

## Alcance

### 1. Error contracts

| Escenario | Código | Detalle |
| :--- | :--- | :--- |
| Referencia vacía (truco sin `skeleton_trick_histograms`) | `422` | `{"detail":"no reference histograms for trick X","missing_metrics":[…]}` |
| Video corrupto / no decodificable | job `failed` | `{"error":"video_unreadable","reason":"…"}` |
| Sin skeleton detectable | job `done` + `skipped` | `result_json.failed="low_quality"`, card sigue "Not analyzed" |
| Confianza de fase < 0.7 | job `done` + `DESCONOCIDO` | FE abre modal manual |
| LSTM sin clasificar | job `done` + `trick_label=null` | FE pregunta el nombre del truco |

### 2. Reprocessing

- Re-upload de un video ya analizado → el FE pregunta **"¿Reprocesar?"**; **no** se reprocesa
  automáticamente salvo video corrupto.
- Endpoint de reproceso idempotente (reusa `POST /api/analysis/videos/{id}/analyze`).

### 3. Quality gates

- SLA del análisis **< 1 min** (pool de workers, batch de landmarks).
- **One analysis at a time** (lock por video/cola).
- Tests: fake landmarks + seed de `skeleton_trick_histograms` + LSTM stub; cobertura ≥ 80%;
  test DBs `pole_api_testing` / `skeleton_data_testing` / `analysis_db_testing`.
- Reintroducir la nota de detección automática en `pixi.toml` `test-hardening` (fue removida).

## Tickets (candidatos)

- [ ] **PAIML-POLE-API-053** — Error contracts unificados + tests por escenario.
- [ ] **PAIML-POLE-API-054** — Reprocessing idempotente + prompt FE.
- [ ] **PAIML-POLE-API-055** — Quality gates: SLA < 1 min, one-analysis-at-a-time, nota
      `test-hardening`.

## Dependencias

- Fases 16-18.

## Criterios de aceptación

- Matriz de errores probada; reproceso idempotente; SLA < 1 min; cobertura ≥ 80%.