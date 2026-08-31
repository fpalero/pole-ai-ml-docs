# Fase 4 — Crawler slice — Crawl + QC — ✅ DONE

> Plan maestro: [PLAN.md](PLAN.md)

## Alcance

- `POST /api/crawler/jobs` (crawl desde hashtags/cuenta).
- `GET /api/crawler/jobs/{id}` (progreso), `GET /api/crawler/posts` (lista posts), 
  `GET /api/crawler/posts/{id}` (detalle post con sources).
- `POST /api/crawler/posts/{id}/qc`, `GET /api/crawler/posts/{id}/qc-status`.
- `POST /api/crawler/jobs/{id}/cancel` (cancel job + rollback).

## Estado

- **DONE** — crawl/QC operativos.

## Dependencias

- Fases 1-2.

## Criterios de aceptación

- Crawl → QC → cancel con rollback probados.