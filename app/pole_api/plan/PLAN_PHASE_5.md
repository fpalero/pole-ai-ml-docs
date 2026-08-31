# Fase 5 — Video slice — Upload + auto-embed — ✅ DONE

> Plan maestro: [PLAN.md](PLAN.md)

## Alcance

- `POST /api/video/classes/{id}/upload` (multipart), `GET /api/video/classes/{id}/videos`.
- Auto-embed tras upload (`stride` config), `GET /api/video/classes/{id}/embed-status`.
- `GET /api/video/classes/{id}/clips`, `GET /api/video/clips/pending-counts`.

## Estado

- **DONE** — upload + auto-embed operativos.

## Dependencias

- Fases 1-3.

## Criterios de aceptación

- Upload → auto-embed → clips probados.