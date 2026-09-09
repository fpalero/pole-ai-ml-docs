# Fase 34 — Unified image endpoint via path-hash (`GET /api/images/{hash}`) — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Ticket: [`phase-34-unified-images/PAIML-POLE-API-106.md`](../phase-34-unified-images/PAIML-POLE-API-106.md)
> Origen: staging QA (analyst chatbot RAG turns) — RAG answers citing book
> figures render as `[]` in the FE. Root cause verified on staging
> (`ipsf-server`, namespace `pole-ai`); user-approved fix: unified
> hash-addressed image endpoint.

## Contexto

Cadena de fallo verificada en staging:

- Chroma `image_path` = `data/_OceanofPDF.../file-0343-04.png` (ruta
  relativa, sin segmento db).
- `pole_coach/nodes/formatter.py:119` copia la ruta cruda en `src`.
- `src/analyst_chatbot/rag_images.py` solo sirve `<data_dir>/<db>/<file>`
  con `db ∈ (pole, calisthenics, psychology, biomechanics)`; los ficheros
  reales viven en `/data/rag/_OceanofPDF.../`.
- El LLM fabrica `/api/rag-images/data/...` (`db=data` inválido) → 404.
- `_coerce_image_block` descarta `src` con `/data`; el sanitizer loguea
  `server path leak after sanitize; scrubbing`; el FE recibe `[]`.

El esquema de direccionamiento (rutas fs como URLs públicas + rutas por
db sobre ficheros sin db) no tiene arreglo parcial: se sustituye por
direccionamiento opaco por hash.

## Scope

- Nuevo endpoint unificado `GET /api/images/{hash}?token=` con
  `hash = sha256(root_id:relative_path)[:32]`.
- Registry L1 in-memory + L2 Redis poblado desde `ALLOWED_ROOTS =
  [/data/rag, /data/uploads, /data/analysis_uploads]` (env-overridable).
- `formatter.py:119` emite URLs hash, nunca rutas crudas (el strip de
  `/data/` + sanitizer quedan como defense-in-depth).
- Rutas legacy `rag-images` → `301` con header `Deprecation` durante una
  release; hashes desconocidos → `410 {code: image_gone}`.
- ADRs: WHY hash-by-path, WHY Redis+memory, WHY 301-compat (en el ticket).

## Tasks

- Router `src/analyst_chatbot/images.py`: auth por chat-token (mismo seam
  que rutas existentes), lookup L1 → L2 → registro on-demand, bytes con
  `Content-Type` por sufijo + `Cache-Control: public, max-age=86400,
  immutable`.
- Registry (`register`/`resolve`/`warm`): walk solo-filenames, warm L1
  desde L2, scan de roots solo con L2 vacío; fail-closed en traversal
  (`..`, symlinks fuera del root → 410).
- Compat legacy: `301` → URL unificada + contador de sunset; test de
  sunset que fuerce el ticket de limpieza de la release siguiente.
- Prompt/guard del analista: `src` opacos, nunca fabricar
  `/api/rag-images/data/…`; test de regresión no-`/data/` en
  replies/blocks.
- Tests `app/pole_api/tests/test_images_unified*.py` + docs (`ENV_VARS.md`:
  `ALLOWED_ROOTS`, `IMAGES_*`; `slices.md`: entrada del endpoint).

## Endpoints

| Método + ruta | Auth | Éxito | Errores |
| :--- | :--- | :--- | :--- |
| `GET /api/images/{hash}?token=` | chat-token | `200` bytes (`Content-Type` por sufijo, `Cache-Control: immutable`) | `401/403` sin token; `410 {code:image_gone}` hash desconocido |
| `GET /api/rag-images/<db>/<file>` (legacy, una release) | chat-token | `301` → `/api/images/{hash}` + `Deprecation: true` | `401/403`; `410` si el fichero no resuelve en el registry |

## Dependencies

- **Blocks:** —
- **Blocked By:** — (Redis ya requerido por el stack; sin migraciones).

## Acceptance

- **UC-01 — figura RAG rinde:** `image.src = /api/images/{32-hex}`;
  `GET` con token → `200` + bytes; la card del FE rinde (no `[]`).
- **UC-02 — sin leaks:** ningún `/data/` en replies/blocks/chips en el
  rerun de la batería (40 preguntas); contador `scrubbing` a cero en
  turnos de imagen.
- **UC-03 — compat legacy:** ruta vieja → `301` → `200`; hash
  desconocido → `410 {code: image_gone}`; sin auth → `401/403`.
- **UC-04 — multi-réplica:** hash registrado en réplica A resuelve en B
  (L2 Redis); restart re-warma L1 desde L2 sin rescan completo.
- `pixi run test-api` verde, cobertura ≥ 80%; verificación en staging
  (ns `pole-ai`): 200 interno + vía ingress, 301 legacy, rerun de
  preguntas con imagen.
