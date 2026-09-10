# Fase 39 — staging-gate residuals (Phase 36 gate, 9-question run 2026-09-10) — 📋 PLANNED (117, 118)

> Plan maestro: [PLAN.md](../PLAN.md) · Tickets:
> [`phase-39-staging-gate-residuals/PAIML-POLE-API-117.md`](../phase-39-staging-gate-residuals/PAIML-POLE-API-117.md) ·
> [`phase-39-staging-gate-residuals/PAIML-POLE-API-118.md`](../phase-39-staging-gate-residuals/PAIML-POLE-API-118.md)
> Origen: Phase 36 staging gate (staging image `8425896` FRESH) — 9-question
> run, batches 1–3, 2026-09-10. Evidence:
> `app/pole_analyst/test-results/coach-150q/batch1-20260910-231630`,
> `batch2-20260910-233800`, `batch3-20260910-233736` (+ `/tmp` backups).
> Numeración: fase 39 porque la 38 la reclama el lane paralelo 116
> (supergraph routing residuals, sin mergear); tickets 117/118 (114+115
> consumidos, 116 reservado en el lane paralelo).

## 1. Contexto

Dos residuos cualitativos del gate, ambos independientes entre sí:

- **117 (Q3 batch-1, unknown-trick):** *"I can do the moonflip-9000, what
  should I try next?"* resuelve `unknown` sin fabricar (bien), pero el
  query-graph renderiza el fallback genérico desnudo (*"I couldn't build
  full coaching advice…"*, 0 tool calls) en vez de la guía explícita
  *"Unknown trick 'moonflip-9000'…"* que solo existe en
  `gating.resolve_trick` + el finish path de readiness.
- **118 (Q9 batch-3, M-codes):** el agente pasa códigos `M-01..M-05` donde
  `metric_deep_dive` espera nombres → primera llamada falla con
  `metric 'M-05' not found …; available metrics: angular_speed, body_tilt,
  …` (`ok:false`, 10/11 tools OK). La precedencia de vídeo se mantuvo
  (handspring, sin secuestro de Butterfly).

### ADR — WHY dos tickets y no uno

Los dos fallos viven en seams distintos (117: ruteo/respuesta del
query-graph para trucos desconocidos; 118: contrato de argumentos de
`metric_deep_dive`) y ninguno depende del otro. Un solo ticket invitaría a
un fix acoplado; dos tickets auto-contenidos permiten lanes paralelos y
re-runs Q3/Q9 independientes. Ambos exigen no-fabricación: 117 nunca debe
inventar transiciones para un truco desconocido; 118 nunca debe inventar
nombres de métrica fuera del vocabulario del vídeo.

## 2. Scope

- **117:** rutar turnos de progresión con truco desconocido a readiness,
  o añadir reply explícito de unknown-trick en el fallback del query
  (fraseo de progresión + mención resoluble-pero-desconocida). Sin
  fabricar transiciones.
- **118:** normalizar M-codes a nombres antes de la llamada a insights
  (tool spec, prompt, o capa de mapeo en el facade).
- **Fuera de scope:** cambios en el catálogo (447 movimientos, intacto),
  reentrenos, trabajo FE, full-150 run.

## 3. Tasks

- [ ] 117: reply explícito unknown-trick en path query-fallback (o ruteo
  a readiness) + tests + re-run Q3.
- [ ] 118: mapeo M-code→nombre pre-insights + tests + re-run Q9.

## 4. Endpoints

Sin endpoints nuevos. Superficie afectada (contrato interno):

| Seam | Entrada | Salida |
| :--- | :--- | :--- |
| query-graph fallback / readiness (`packages/pole_coach`) | turno progresión, truco unknown | reply explícito `Unknown trick '…'…`, 0 fabricación |
| `metric_deep_dive` facade/spec/prompt | `M-01..M-05` | nombre de métrica válido del vídeo |

## 5. Dependencies & Acceptance

- **Blocks:** — (117 y 118 independientes, sin bloqueos).
- **Blocked By:** — (staging `8425896` como base del re-run).

Acceptance (resumen; detalle por ticket):

- **UC-01 (117):** re-run Q3 → reply explícito unknown-trick con fraseo
  de progresión; cero transiciones fabricadas; `pixi run test-api` verde.
- **UC-02 (118):** re-run Q9 → `metric_deep_dive` sin `analysis_failed`,
  turno no ABANDONED; precedencia de vídeo intacta;
  `pixi run test-api` verde.
