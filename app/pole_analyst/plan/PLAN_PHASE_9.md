# Fase 9 — Results View: fases + feedback + error frames — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md) · Feature: detección automática de fases (handspring) — FE `pole_analyst`

## Contexto

Tras `done`, el atleta ve el **resultado del análisis**: las fases detectadas
(ENTRADA/EJECUCIÓN/SALIDA) con sus frames, el feedback de ejecución y las imágenes de frames de
error. Sustituye/complementa los tabs Summary/Histogram de la Fase 4 con una vista orientada al atleta.

## Alcance

### 1. Resultado de fases

- `GET /api/analysis/videos/{id}/summary` → fases detectadas con `start/end` + confianza.
- Timeline visual de fases (ENTRADA → EJECUCIÓN → SALIDA) sobre la línea de tiempo del video.

### 2. Feedback de ejecución

- Métricas (5 usadas) con score 0-100 y desviación vs cohort (`z_mean`).
- Feedback textual por métrica (auto-generado en backend o por el chatbot).

### 3. Error frames

- `detections[].frame_image_path` → imágenes de frames críticos (una por punto `|z| > 1`), con el
  nombre de la métrica y fase.

## Endpoints consumidos

| Endpoint | Método | Uso |
| :--- | :--- | :--- |
| `GET /api/analysis/videos/{id}/summary` | GET | Fases, scores, detections |
| `GET /api/analysis/videos/{id}/histogram` | GET | Curvas por métrica |

## Tickets (candidatos)

- [ ] **PAIML-POLE-ANALYST-031** — App/Domain: DTOs de summary (fases + scores + detections).
- [ ] **PAIML-POLE-ANALYST-032** — Presentation: ResultsView (timeline de fases, feedback, error frames).
      Blocked by backend `PLAN_PHASE_3`.

## Dependencias

- **Blocked By:** backend `pola_api` fases 1-3; FE fase 8 (trigger + progreso).

## Criterios de aceptación

- [ ] Tras `done` se muestra la timeline de fases detectadas.
- [ ] Se muestran los error frames con métrica/fase asociada.
- [ ] Cobertura ≥ 80% en módulos nuevos.