# Fase 8 — Upload + Progress Panel (análisis con detección de fases) — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md) · Feature: detección automática de fases (handspring) — FE `pole_analyst`

## Contexto

El flujo de análisis del atleta gana un **progress panel** con etapas visibles para la detección
automática de fases. La Fase 3 (upload + librería) y la Fase 4 (detail tabs) ya existen como plan;
esta fase **redefine el flujo de análisis** para integrar la nueva pipeline backend:
`Extraction → Processing → Phase detection → Classification & analysis → Summary`.

## Alcance

### 1. Trigger de análisis con etapas

- `POST /api/analysis/videos/{id}/analyze` (202 job) dispara el pipeline.
- Progress panel muestra las **5 etapas** con estado (`pending` / `running` / `done` / `failed`):
  1. Extraction (MediaPipe landmarks)
  2. Processing (histogramas por métrica)
  3. Phase detection (detección automática ENTRADA/EJECUCIÓN/SALIDA)
  4. Classification & analysis (LSTM + feedback)
  5. Summary
- El FE deriva el estado de cada etapa del `result_json`/progress del job (reutiliza `jobs-store`).

### 2. Eventos del job

- La etapa de detección informa `detected=true` + fases candidatas con confianza, o `detected=false`
  (confianza < 0.7 → `DESCONOCIDO`).
- La etapa de clasificación informa `trick_label` (o `null` si el LSTM falla).

## Endpoints consumidos

| Endpoint | Método | Uso |
| :--- | :--- | :--- |
| `POST /api/analysis/videos/{id}/analyze` | POST | Trigger análisis (202) |
| `GET /api/analysis/jobs/{job_id}` | GET | Poll del job + etapas |
| `GET /api/analysis/videos/{id}/summary` | GET | Resultado tras `done` |

## Tickets (candidatos)

- [ ] **PAIML-POLE-ANALYST-029** — App/Domain: DTOs de job stages + mapeo de etapas.
- [ ] **PAIML-POLE-ANALYST-030** — Presentation: ProgressPanel (5 etapas) + trigger de análisis.
      Blocked by backend `PLAN_PHASE_3`.

## Dependencias

- **Blocked By:** backend `pola_api` fases 1-3 (rename, referencias, detección).

## Criterios de aceptación

- [ ] Al lanzar análisis se muestra el progress panel con las 5 etapas.
- [ ] Las etapas reflejan el estado real del job.
- [ ] Cobertura ≥ 80% en módulos nuevos.