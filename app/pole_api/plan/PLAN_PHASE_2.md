# Fase 2 — Training slice — Classes CRUD — ✅ DONE

> Plan maestro: [PLAN.md](PLAN.md)

## Alcance

- `POST/GET /api/training/classes`, `GET/PATCH/DELETE /api/training/classes/{id}`.
- Clases stateless (sin status field; estado derivado de entidades).
- Tracker `N` → `E` en pipeline, garbage cleanup en cancel/fail.
- Validación de duplicados (nombre + hashtags).

## Estado

- **DONE** — CRUD de clases operativo.

## Dependencias

- Fase 1.

## Criterios de aceptación

- CRUD clases + tracker + validación probados.