# Fase 29 — Staging QA follow-ups (image endpoint + path-leak strip + `segment_insight` trim + failed-turn signal + video resolution end-to-end) — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Origen: phase-23 staging QA gate (40-question battery
> a través del FE real). Evidencia del tester (local, no commiteada):
> `/tmp/opencode/staging-battery/` (`summary.json`, `ws-triage.json`, `run.log`) y
> `/tmp/opencode/tool08-repro/` (`tool08-frames.json`) para el bundle 1 (093);
> `/tmp/opencode/staging-rerun2/` (`summary.json`, `replies.json`, `errors.json`,
> `TOOL-*.png`) para el bundle 2 (094).

## Contexto

Dos bundles backend bajo la misma fase:

**Bundle 1 (093) — cuatro causas raíz del staging gate:**

- (a) Los artefactos de análisis (frames, histogramas bajo `/data/uploads/…`) se referencian
  por rutas container-local que el navegador no puede cargar — turnos TOOL-04/TOOL-18 rinden
  solo `md` (`missing cards: image` en `summary.json`).
- (b) Las rutas absolutas del servidor nunca deben aparecer en prosa visible (TOOL-04 rindió
  bullets `/data/uploads/…`).
- (c) El payload de la tool `segment_insight` infla la llamada LLM de follow-up a ~112k tokens
  (OpenRouter 402 → turno ABANDONED); la pregunta TOOL-08
  ("What happened during the execution phase (seconds 2-6)…") termina en fallback genérico
  (`tool08-frames.json`: `agent_reply` con "I'm having trouble understanding…", `tool_calls: []`).
- (d) Los turnos ABANDONED/error deben emitir un estado de error explícito legible por máquina,
  no chip `Completed` + fallback genérico (`tool08-frames.json`: `"chipFinal": "Completed"`).

**Bundle 2 (094) — video resolution end-to-end (staging rerun2):**

- (e) `AnalysisVideoRepository.get()`
  (`app/pole_api/src/analysis/repositories/analysis_repository.py:39`) solo intenta
  ObjectId → exact filename → prefix filename, así que nombres de truco como
  `handspring`/`ayesha` no matchean ficheros como `bodybyfran_handspring.mp4` /
  `aysha.mp4` — faltan fallbacks de substring-filename y `trick_label`
  (verificados live: ambos devuelven el doc correcto). Sin fuzzy-spelling
  (deferral ayesha, ver nota FUTURE abajo).
- (f) El LLM analista fabrica IDs placeholder literales (`handspring_video`,
  `ayesha_video`) que bypasean el resolver (turnos TOOL-11/12/13) — fix:
  resolución `list_videos`-first, nunca pasar ids fabricados.
- (g) Inconsistencia por tool: `segment_insight` / `get_coach_summary` /
  `get_coach_pose` resuelven mientras `extract_frames` / `crop` /
  `metric_deep_dive` / `frame_pose` / `compare_sessions` dicen "not analyzed"
  en videos analizados — unificar en un solo `resolve_video()`.
- (h) ADR de la estrategia de resolución + nota de la dualidad `str`/`ObjectId`
  de `video_id`.
- (i) Desambiguación: con 2+ videos del mismo truco en staging,
  "my handspring video" resuelve al latest y lo nombra.

## Tickets

| Ticket | Scope | Estado |
| :--- | :--- | :--- |
| `PAIML-POLE-API-093` | Endpoint HTTP autenticado de artefactos + `image.src` como URL; strip de `/data/` en prosa; trim de `segment_insight` + cap `max_tokens`; señal de error explícita en turnos ABANDONED | 📋 PLANNED |
| `PAIML-POLE-API-094` | Video resolution end-to-end: fallbacks substring-filename + `trick_label` en `AnalysisVideoRepository.get()`; guard placeholder-ID (`list_videos`-first); unificación per-tool (`resolve_video()`); ADR de resolución (+ dualidad `str`/`ObjectId`); desambiguación latest-wins + name-it | 📋 PLANNED |

## Tasks

**Bundle 1 (093):**

- Servir artefactos (frames, histogramas) por endpoint HTTP autenticado; `image.src` = URL
  alcanzable, nunca ruta de contenedor.
- Post-procesar `reply`/síntesis `md` para eliminar rutas absolutas (`/data/…`); helper de
  regresión (ningún `reply`/`blocks[].content` contiene `/data/`).
- Devolver solo el slice pedido en `segment_insight` (truncar/resumir, capar arrays) y capar
  `max_tokens` del follow-up; documentar los caps.
- Señal de error legible por máquina en el frame `agent_reply` para turnos ABANDONED/error
  (compatible hacia atrás; documentar el shape para el FE).
- Tests en `app/pole_api/tests/test_analyst_chatbot*.py` para (a)–(d).

**Bundle 2 (094 — video resolution):**

- Extender `AnalysisVideoRepository.get()` con fallbacks substring-filename y
  `trick_label` tras la cadena existente (sin fuzzy-spelling).
- Guard placeholder-ID: re-resolución `list_videos`-first; el prompt exige ids
  resueltos, nunca literales inventados (TOOL-11/12/13).
- Unificar todas las video-tools en un `resolve_video()` compartido
  (paridad `segment_insight` / `get_coach_summary` / `get_coach_pose` /
  `extract_frames` / `crop` / `metric_deep_dive` / `frame_pose` /
  `compare_sessions`).
- ADR de resolución (orden de fallbacks, `list_videos`-first, dualidad
  `str`/`ObjectId` de `video_id`, latest-wins + name-it, deferral fuzzy).
- Desambiguación latest-wins (`created_at`) nombrando el fichero elegido.
- Tests en `app/pole_api/tests/test_analyst_chatbot*.py` para (e)–(i).

## Acceptance

**Bundle 1 (093):**

- El endpoint sirve bytes con auth (200 + bytes; 404 desconocido; 401/403 sin auth);
  `image.src` son URLs HTTP(S).
- Ningún string `/data/` en replies en el rerun de la batería de 40 preguntas.
- Los turnos clase-TOOL-08 entran en presupuesto (sin 402/ABANDONED por payload).
- ABANDONED expone estado de error legible por máquina (no `Completed` + fallback).
- `pixi run test-api` verde, cobertura ≥ 80%.

**Bundle 2 (094):**

- `handspring` resuelve `bodybyfran_handspring.mp4` (substring) y el fallback
  `trick_label` resuelve el doc de `aysha.mp4`.
- Turnos clase-TOOL-11/12/13 ya no pasan ids `*_video` fabricados (resolución
  `list_videos`-first).
- Paridad cross-tool: la misma expresión resuelve igual en las ocho tools; ninguna
  dice "not analyzed" en un video que otra resuelve.
- ADR existe y enlazado aquí (fallbacks, `list_videos`-first, dualidad
  `str`/`ObjectId`, latest-wins + name-it, deferral fuzzy).
- Con 2+ videos del mismo truco, "my handspring video" resuelve al latest y lo nombra.
- `pixi run test-api` verde, cobertura ≥ 80%.

## FUTURE — ayesha deferral (no ticket, no code)

> Classifier/cohort support is handspring-only, so TOOL-06/11/20 (ayesha
> questions) are deferred; the staging gate runs handspring variants until an
> ayesha cohort exists. No fuzzy-spelling matching is required in 094 for the
> same reason (ayesha testing deferred).

## Dependencies

- **Blocks:** `pole_analyst` Phase 24 (`PAIML-POLE-ANALYST-073` — el FE consume la señal (d)
  y adopta las URLs (a)). `PAIML-POLE-API-094` blocks nothing (backend-only; FE sin
  cambio de contrato).
- **Blocked By:** None.
