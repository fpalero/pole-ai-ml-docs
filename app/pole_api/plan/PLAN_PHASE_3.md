# Fase 3 — Training slice — Process + Embed + Jobs — ✅ DONE

> Plan maestro: [PLAN.md](PLAN.md)

## Alcance

- `POST /api/training/classes/{id}/process` (windows + embed), `POST /api/training/classes/{id}/embed`.
- `POST /api/training/classes/{id}/train` (entrenar modelo).
- `GET /api/training/classes/{id}/jobs` (jobs del pipeline con `history`).

## Estado

- **DONE** — process/embed/train operativos.

## Dependencias

- Fases 1-2.

## Criterios de aceptación

- Pipeline N→E→M probado con jobs y history.