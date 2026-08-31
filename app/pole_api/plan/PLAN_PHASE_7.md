# Fase 7 — Training slice — Model registry + Retrain — ✅ DONE

> Plan maestro: [PLAN.md](PLAN.md)

## Alcance

- `GET /api/training/models` (lista runs), `GET /api/training/models/{run_id}` (detalle run + deltas).
- `POST /api/training/models/{run_id}/approve` (activate), `POST /api/training/classes/{id}/retrain`.
- `GET /api/training/models/active.json` (baseline activo).

## Estado

- **DONE** — registry + retrain operativos.

## Dependencias

- Fases 1-3.

## Criterios de aceptación

- Registry runs + approve + retrain probados.