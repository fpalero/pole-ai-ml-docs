# Fase 43 — staging-gate residuals: RE-04 T2 citations + RE-05 T3 CTA + VA tail-latency (22/25 → 25/25)

> Plan maestro: [PLAN.md](../PLAN.md) · Tickets:
> [`phase-43-staging-gate-residuals/PAIML-POLE-API-146.md`](../phase-43-staging-gate-residuals/PAIML-POLE-API-146.md) ·
> [`phase-43-staging-gate-residuals/PAIML-POLE-API-147.md`](../phase-43-staging-gate-residuals/PAIML-POLE-API-147.md) ·
> [`phase-43-staging-gate-residuals/PAIML-POLE-API-148.md`](../phase-43-staging-gate-residuals/PAIML-POLE-API-148.md)
> Origen: staging SAMPLE-5 RUN_ID `20260924-163713` — **22/25 PASS, GATE FAIL**
> (bar 5/5 per flow): VA 4/5 (VA-05 timeout), RE 3/5 (RE-04 T2-citations +
> RE-05 missing-CTA); RE-01/RE-03 fixed by 144.
> Evidencia: `app/pole_analyst/test-results/coach-150q/20260924-163713/` +
> staging logs `supergraph invoke exceeded 30.0s budget; delegating` every turn.
> Numeración: fase 43 (42 es la última existente). 146/147/148 independientes
> entre sí (ninguno bloquea a otro; secuenciar solo por conflictos de fichero
> compartido, no por dependencia).

## 1. Contexto

Tras 144 (tier-marker emission en paths ReAct-delegados, RE-01/RE-04) y 145
(spec/harness hardening, test-only), el gate de staging SAMPLE-5
(`20260924-163713`) queda en **22/25**. Residuales, tres clases:

- **RE-04 (Jade T2 citations):** "What prerequisites am I missing for the
  Jade split?" → `blocks: [md]`, sin citas T2. Candidatos: guards
  136-backstop en `coach_providers.py:793-856` (owner-scope `810-811`) que
  devuelven `[]`, o early-return T2 en `answer_shaping.py:1604-1640` que deja
  shaped-untouched → `get_readiness_prerequisites` no dispara con
  owned/prereq arrays → ticket 146.
- **RE-05 (Brass Monkey T3 CTA):** "Am I ready to attempt Brass Monkey on
  spin?" → sin `readiness_cta` en T3 zero-data (dependencia de la rama
  corpus-content `answer_shaping.py:1642-1658`) + `rag_proof` false pese a
  `query_*` calls (successful-tool filter / error guard) → ticket 147.
- **VA-05 (tail-latency flake):** "Review my latest video: was my body angle
  consistent from ENTRANCE to EXIT?" → timeout. Flake migró VA-04→VA-05
  (misma firma, distinto turno): supergraph 30s blow-every-turn → cadena
  ReAct → overrun del budget FE 360s; sospecha OpenRouter
  `deepseek-v4-flash` tail → ticket 148 (retry gate-side test-only + record
  progress-frames futuro).

Decisión de producto (heredada de 42): merge a `develop` auto-despliega a
staging — PRs solo con gate local verde; docs-first (tickets + docs
atómicos en `pole-ai-ml-docs`).

## 2. Alcance

| # | Ticket | Ficheros / cambio |
| :- | :--- | :--- |
| 146 | RE-04 Jade T2 citations | `coach_providers.py:793-856` (forense guards + owner-scope `810-811`) vs `answer_shaping.py:1604-1640` (T2 early-return); guard-trip logging/counters; fix pierna disparada para que `get_readiness_prerequisites` dispare con owned/prereq (o registro evidenciado de RAG-only T2 intencional) |
| 147 | RE-05 Brass Monkey T3 CTA | `answer_shaping.py:1641-1731` (emisión estructural CTA sin dependencia `1642-1658`); `blocks.py:550` (`_coerce_readiness_cta_block` nunca dropea); fix successful-tool filter / error guard tras `rag_proof` false |
| 148 | VA tail-latency flake | harness test-only: retry por turno solo-timeout (precedente 132/145); record server progress-frames como FUTURO (sin código prod) |

Tests herméticos por fix + gate local SAMPLE-5 25/25 (no staging).

## 3. Tareas

- [ ] 146: forense qué guard devuelve `[]`/shaped-untouched en turnos Jade;
      logging/counters de guard-trip; fix pierna disparada (owned/prereq
      poblados) o registro de RAG-only intencional.
- [ ] 147: CTA estructural T3 zero-data; garantía `_coerce`; fix `rag_proof`
      filter/guard; ask-once 2º turno.
- [ ] 148: retry gate-side por turno timeout-only (test-only, acotado, sin
      inflar budgets); flake VA-04→VA-05 documentado como tail; record
      progress-frames futuro.

## 4. Criterios de aceptación

- Gate local SAMPLE-5 **25/25 verde** (k3s-local; staging solo a gate time).
- 146: Jade-split Q → `md` + `retrieval_hits` con citas owned/prereq.
- 147: Brass Monkey Q → `md` + `retrieval_hits` + CTA + ask-once 2º turno
  con cero corpus; `rag_proof` true con `query_*` exitosos.
- 148: turno timeout reintentado una vez (test-only) → `md` +
  `analysis_link`; budgets intactos; cero código prod.
- Sin regresiones (125/134/135/136/140/141/144 suites verdes; T1 intacto).

## 5. Plan de validación (local-first, obligatorio)

1. Hermetic replays por ticket (runs repetidos, determinismo).
2. `pixi run test-api` verde (≥80% coverage).
3. Live battery proof diferida a gate time (staging):
   `npx playwright test coach-150q.spec.ts --workers=1 -g "COACH7-(RE-04|RE-05|VA-05)"`.
4. Nunca contra staging/prod DBs (guard `_testing`; remote-backend mode
   contra el stack local).

## 6. Fuera de alcance (futuro)

- Server-side progress-frames durante cadenas ReAct largas (148 lo registra
  como FUTURO, sin implementación).
- Inflar budgets supergraph 30s / FE 360s para "arreglar" el flake
  (explícitamente rechazado en 148).
