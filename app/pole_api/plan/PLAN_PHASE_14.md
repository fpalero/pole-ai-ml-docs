# Fase 14 — Histogram status flag + counts — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md)

## Contexto

`pole_fe` (Phase 9) necesita saber el estado de histograma por video y los counts de clips
(`HISTO` status derivado, sin N+1).

## Alcance detallado

- Flag `histogram_processed` (bool) en los docs de video/clip.
- `GET /api/video/classes/{id}/histo-counts` (o extend de clips counts) → `X-Count-*` headers con
  conteos por estado (`EXTRACTED` / `HISTO`).
- Sin N+1: agrega con un solo query.

### Estado

- **PLANNED** (detalle completo en el PLAN.md original §10).
- Tickets backend: `PAIML-POLA-API-036..038` (bloquean `PAIML-POLE-FE-005/006`).

## Dependencias

- Fases 5-6 (video slice).

## Criterios de aceptación

- Flag + counts sin N+1; FE de Phase 9 los consume.