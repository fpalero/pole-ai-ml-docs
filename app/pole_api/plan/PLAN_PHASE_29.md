# Fase 29 — Staging QA follow-ups (image endpoint + path-leak strip + `segment_insight` trim + failed-turn signal) — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Origen: phase-23 staging QA gate (40-question battery
> a través del FE real). Evidencia del tester (local, no commiteada):
> `/tmp/opencode/staging-battery/` (`summary.json`, `ws-triage.json`, `run.log`) y
> `/tmp/opencode/tool08-repro/` (`tool08-frames.json`).

## Contexto

Cuatro causas raíz establecidas por el staging gate, un solo bundle backend:

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

## Tickets

| Ticket | Scope | Estado |
| :--- | :--- | :--- |
| `PAIML-POLE-API-093` | Endpoint HTTP autenticado de artefactos + `image.src` como URL; strip de `/data/` en prosa; trim de `segment_insight` + cap `max_tokens`; señal de error explícita en turnos ABANDONED | 📋 PLANNED |

## Tasks

- Servir artefactos (frames, histogramas) por endpoint HTTP autenticado; `image.src` = URL
  alcanzable, nunca ruta de contenedor.
- Post-procesar `reply`/síntesis `md` para eliminar rutas absolutas (`/data/…`); helper de
  regresión (ningún `reply`/`blocks[].content` contiene `/data/`).
- Devolver solo el slice pedido en `segment_insight` (truncar/resumir, capar arrays) y capar
  `max_tokens` del follow-up; documentar los caps.
- Señal de error legible por máquina en el frame `agent_reply` para turnos ABANDONED/error
  (compatible hacia atrás; documentar el shape para el FE).
- Tests en `app/pole_api/tests/test_analyst_chatbot*.py` para (a)–(d).

## Acceptance

- El endpoint sirve bytes con auth (200 + bytes; 404 desconocido; 401/403 sin auth);
  `image.src` son URLs HTTP(S).
- Ningún string `/data/` en replies en el rerun de la batería de 40 preguntas.
- Los turnos clase-TOOL-08 entran en presupuesto (sin 402/ABANDONED por payload).
- ABANDONED expone estado de error legible por máquina (no `Completed` + fallback).
- `pixi run test-api` verde, cobertura ≥ 80%.

## Dependencies

- **Blocks:** `pole_analyst` Phase 24 (`PAIML-POLE-ANALYST-073` — el FE consume la señal (d)
  y adopta las URLs (a)).
- **Blocked By:** None.
