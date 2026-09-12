# Fase 42 — coach 25-battery gate: ground all unanswered flows (FC1–FC6)

> Plan maestro: [PLAN.md](../PLAN.md) · Tickets:
> [`phase-42-coach-gate-25/PAIML-POLE-API-122.md`](../phase-42-coach-gate-25/PAIML-POLE-API-122.md) ·
> [`phase-42-coach-gate-25/PAIML-POLE-API-123.md`](../phase-42-coach-gate-25/PAIML-POLE-API-123.md) ·
> [`phase-42-coach-gate-25/PAIML-POLE-API-124.md`](../phase-42-coach-gate-25/PAIML-POLE-API-124.md) ·
> [`phase-42-coach-gate-25/PAIML-POLE-API-125.md`](../phase-42-coach-gate-25/PAIML-POLE-API-125.md) ·
> [`phase-42-coach-gate-25/PAIML-POLE-API-126.md`](../phase-42-coach-gate-25/PAIML-POLE-API-126.md)
> Nota (2026-09-12): post-PR-#322 staging run `sample5-e743e61-20260912-083119` = **13/25**;
> residuals split into 124 (FE renderer+image), 125 (prompt/tool-selection), 126 (WS guard).
> Origen: SAMPLE-5 battery (2026-09-11T05:57Z, `RUN_ID sample5-post116-20260911-055758`,
> staging image `9c88ab0`) — **8/25 PASS, GATE FAIL** (bar 5/5 per flow).
> Evidencia: `app/pole_analyst/test-results/coach-150q/sample5-post116-20260911-055758/` +
> merged 25-row set `/tmp/coach7-MERGED-*.jsonl` + `/tmp/coach7-run{,2}-sample5-*.log`.
> Numeración: fase 42 (41 es la última existente). 122 = TODAS las correcciones FC1–FC6 en
> un único PR; 123 = deep-dive FUTURO del porqué los hashes de imagen se vuelven no verificables
> (síntoma ya tratado con el fail-closed en 122).

## 1. Contexto

> **2026-09-11:** FC1 (tool-proof progress) landed in `pole-ai-ml` develop via direct commit
> `7501edb` (merged on branch `feature/PAIML-POLE-API-122-coach-gate-25`, no PR).
> FC2–FC6 remain in progress on the same branch. Phase flag stays 🟡 PARTIAL.

Tras estabilizar 116/117/118/121, la batería completa SAMPLE-5 (25 preguntas, 5 slices,
barra 5/5) sigue en rojo: 17 de 25 caen en 6 clases de fallo, todas con path de código evidencado:

- **FC1 (PR-01, PR-05):** el wrapper del cerebro supergraph (`services.py:326-333`) hardcodea
  `tool_calls=[]` → la respuesta trae `progress_matrix` real pero sin prueba de tool → la
  aserción `get_progress_matrix called` del spec falla.
- **FC2 (PR-02/03/04, RE-01/02/03/05, VA-03; 8 turns):** sin `video_id`/`trick_name`
  resolvible — `_VIDEO_REFERENCE_RE` (`coach_providers.py:101`) solo cubre
  `video|clip|footage` (VA-03 "last upload" no dispara la leg 115 R2); turns métricas sin
  trick → `fetch_trick_progress` skip (`_common.py:99-101`); readiness sin nodo retrieve →
  `hasRagProof` estructuralmente imposible.
- **FC3 (VA-04, TP-03, IN-02):** gate de imagen (`blocks.py:352-357`) solo dropea en `is False`;
  la rama `None` (import fail `309-310`, resolve exception `316-317`, TOCTOU) deja pasar el
  src crudo `/api/images/<hash>` → 410 → `<img>` roto → aserción `broken images`.
- **FC4 (VA-05, TP-05, IN-04):** sin guard de wall-clock por turno en el WS handler; 30s
  supergraph + 120s ReAct pueden encadenar > 360s (FE budget) → cero frames.
- **FC5 (IN-03):** injury sin trick → `make_pole` (necesita `trick_name`) y `make_coach`
  (necesita ambos contextos) se skipan → disclaimer-only → `hasRagProof` false.
- **FC6 (harness):** `helpers.ts:69` `AbortSignal.timeout(900)` + 1s ping en internet público
  mató el run 1.

## 2. Decisiones de producto (confirmadas por el owner)

1. Respuestas basadas en datos se enrutan por las **herramientas reales** (evidencia de tool,
   no sintética).
2. Modelo local: **`qwen3.8:27b`** (default ollama del repo).
3. Imágenes no verificables se **descartan** (fail-closed); ticket 123 investiga el porqué.
4. El merge a `develop` **auto-despliega a staging** — el PR se sube SOLO con 25/25 verde local.
5. Tickets + docs atómicos en `pole-ai-ml-docs`.

## 3. Alcance (un único PR de código, ticket 122)

| # | Fichero | Cambio |
| :- | :--- | :--- |
| 1 | `coach_providers.py` | extender `_VIDEO_REFERENCE_RE` (upload/session/recording); default latest-video para turns data-oriented; propagar tool evidence del path brain |
| 2 | `services.py` | brain `AgentTurn` con `tool_calls` reales (FC1); guard per-turno WS (FC4) |
| 3 | `blocks.py` / `answer_shaping.py` | fail-closed image gate (FC3) + validación URL en `_image_blocks_from_urls` |
| 4 | `pole_coach/graphs/_common.py` / `progress.py` / readiness | injury coach biomech-only (FC5); retrieve evidence en readiness (FC2) |
| 5 | `app/pole_analyst/e2e/helpers.ts` | ping budget + retry (FC6) |

Tests unitarios por fix + gate local 25/25 (no staging).

## 4. Criterios de aceptación

- Gate local SAMPLE-5 **25/25 verde** (k3s-local + ollama `qwen3.8:27b`).
- Sin regresiones (smoke Q1/Q2, bank #27).
- PR a `pole-ai-ml develop` SOLO tras verde local (auto-deploy staging).

## 5. Plan de validación (local-first, obligatorio)

1. Build → `localhost:5000`, deploy k3s-local (`values-local.yaml`, tags `dev`,
   `imagePullPolicy: Always`), `LLM_PROVIDER=ollama` `OLLAMA_MODEL=qwen3.8:27b`.
2. Seed COACH7-SETUP en DBs locales.
3. Loop `COACH150Q_SAMPLE=5` (workers 1, 360s/turn, RUN_ID único, backup `/tmp` cada 5 turns)
   → triage evidence packet → fix → rebuild → rerun → hasta 25/25.
4. `pixi run test-api` verde (≥80% coverage).
5. Nunca contra staging/prod DBs (guard `_testing`; remote-backend mode contra el stack local).

## 6. Fuera de alcance (futuro)

- PAIML-POLE-API-123: porqué los hashes de imagen se vuelven no verificables
  (TOCTOU vs `None` vs token vs pure-hash — 4 candidatos, correlación con logs).