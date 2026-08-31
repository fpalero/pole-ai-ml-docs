# Fase 15 — Rename `pola_api` → `pole_api` + renames de colecciones — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md) · Feature: detección automática de fases (handspring) — backend

## Contexto

Estandarizar el naming: `pola_api` → **`pole_api`** (directorio, imports, prefijo de tickets
`PAIML-POLA-API` → `PAIML-POLE-API`, bases `pole_api*`). Además renombrar colecciones para reflejar
su función y preparar la nueva colección de histogramas de referencia.

## Alcance

### 1. Rename del paquete/estructura

- `app/pola_api/` → `app/pole_api/`; imports `app.pola_api.*` → `app.pole_api.*`.
- Prefijo de tickets en `PROJECT_VARS.md`: **`PAIML-POLE-API`** (hereda el último número 38).
- Bases de datos: `pole_api` / `pole_api_testing` (renames en config + tests + guard).
- Actualizar referencias: `pixi.toml` tasks, `docker-compose.yml`, AGENTS.md, docs.

### 2. Renames de colecciones (skeleton_data)

| Actual | Nuevo | Contenido |
| :--- | :--- | :--- |
| `skeleton_data.signal_histograms` | `skeleton_data.skeleton_cohort_signals` | cohort stats (`mean`/`std` por métrica y fase) |
| `skeleton_data.skeleton_histograms` | `skeleton_data.skeleton_video_signals` | histogramas por video |

- Actualizar refs: `HistogramRepository` (`COLLECTION_NAME`), `histogram_processor.py`
  (`upsert_cohort_statistics`), consultas, tests. (~101 refs a `signal_histograms`.)

### 3. Nueva colección `skeleton_trick_histograms`

- **NUEVA:** histogramas de **referencia** por truco (una doc por `(trick_label, metric, phase)`):
  `trick_label`, `metric`, `phase` (ENTRADA/EJECUCIÓN/SALIDA), `bins`, `counts`, `total`,
  `last_updated`, `source_count` (nº de clips usados).
- Producida por la Fase 16 (generación de referencias desde clips aprobados) y consumida por la
  Fase 17 (detección de fases).

## Tickets (candidatos)

- [ ] **PAIML-POLE-API-039** — Rename `pola_api` → `pole_api` (paquete + imports + tasks + docs).
- [ ] **PAIML-POLE-API-040** — Rename `signal_histograms` → `skeleton_cohort_signals` y
      `skeleton_histograms` → `skeleton_video_signals`.
- [ ] **PAIML-POLE-API-041** — Crear colección `skeleton_trick_histograms` + modelo + repo.
      (opcional: `PAIML-POLE-API-042` para la CLI de backfill de renames.)

## Dependencias

- Fase 9 (colecciones existentes a renombrar).

## Criterios de aceptación

- Sin refs a `pola_api`/`signal_histograms`/`skeleton_histograms` legacy.
- Colección `skeleton_trick_histograms` creada.
- Tests + guard `_testing` verdes tras renames.