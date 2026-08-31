# Fase 1 — Fundamentals — ✅ DONE

> Plan maestro: [PLAN.md](PLAN.md)

## Alcance

- FastAPI app factory `pola_api`, settings via pydantic-settings (`core/config.py`), CORS, health
  check, request-id + correlation logging.
- MongoDB clients: `pole_api` (app), `skeleton_data` (skeleton/store), connect/init con
  `_testing`-suffix guard para test.
- `core/jobs`: collection + job id pattern (`PJOB-*`), progress callbacks, cancel tokens,
  retry/error isolation; `JobRequest`/`JobResponse` base.
- Shared models y utilidades (datetime, `_testing` guards).

## Estado

- **DONE** — infraestructura base en producción.

## Dependencias

- Ninguna (fundacional).

## Criterios de aceptación

- App arranca, health OK, jobs base funcionales, guard `_testing` activo.