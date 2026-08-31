# Fase 10 — Manual phases modal + LSTM-fail flow + reproceso — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md) · Feature: detección automática de fases (handspring) — FE `pole_analyst`

## Contexto

Cuando la detección automática no es fiable o el LSTM falla, el atleta debe poder **corregir las
fases manualmente** y el sistema debe **preguntar el nombre del truco** si el clasificador no puede
determinarlo. También se gestiona el **reproceso** tras un re-upload.

## Alcance

### 1. Modal de fases manuales

- Si `detected=false` (confianza < 0.7 → `DESCONOCIDO`), se abre un **modal manual** (patrón del
  endpoint existente `PUT /api/training/clips/{video_id}/phase-frames`).
- El usuario arrastra/define los límites ENTRADA / EJECUCIÓN / SALIDA.
- Se re-lanza la fase de classification & analysis con las fases corregidas (job de re-análisis).

### 2. Flujo LSTM falla → preguntar nombre del truco

- Si la clasificación LSTM devuelve `null` (confianza baja), el FE pregunta al atleta el **nombre del
  truco** (input libre con sugerencias de clases existentes).
- El nombre se envía al backend para el feedback/análisis final.

### 3. Reproceso tras re-upload

- Si el usuario sube de nuevo un video ya analizado, el FE pregunta **"¿Reprocesar?"**.
- No se reprocesa automáticamente salvo que el video esté corrupto (error de extracción).

## Endpoints consumidos

| Endpoint | Método | Uso |
| :--- | :--- | :--- |
| `PUT /api/training/clips/{video_id}/phase-frames` | PUT | Fases manuales (existente) |
| `POST /api/analysis/videos/{id}/analyze` | POST | Re-análisis con fases corregidas |

## Tickets (candidatos)

- [ ] **PAIML-POLE-ANALYST-033** — App/Domain: servicios de fases manuales + trick-name + reproceso.
- [ ] **PAIML-POLE-ANALYST-034** — Presentation: modal manual de fases.
- [ ] **PAIML-POLE-ANALYST-035** — Presentation: flujo LSTM-fail (preguntar truco) + prompt de reproceso.
      Blocked by backend `PLAN_PHASE_3` (estado `DESCONOCIDO`/`null`).

## Dependencias

- **Blocked By:** backend `pola_api` fases 1-3; FE fases 8-9.

## Criterios de aceptación

- [ ] Modal manual abre cuando `detected=false`.
- [ ] LSTM fail → prompt de nombre de truco.
- [ ] Re-upload de video analizado → prompt de reproceso (no automático).
- [ ] Cobertura ≥ 80% en módulos nuevos.