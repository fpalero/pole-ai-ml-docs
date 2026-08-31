# Fase 8 — E2E + cross-slice touchpoints — ✅ DONE

> Plan maestro: [PLAN.md](PLAN.md)

## Alcance

- `pixi run test-integration` (aggregator): `test-api` + CLI integration + `test-chatbot-live` +
  FE+BE `fe-e2e` (Playwright), con `_testing`-suffix guard.
- Cross-slice touchpoints E2E (upload → process → embed → train → approve).
- Hardening de eventos de job (persistence del chat, relleno de history).

## Estado

- **DONE** — suite E2E cross-slice operativa.

## Dependencias

- Fases 1-7.

## Criterios de aceptación

- `pixi run test-integration` verde; guard `_testing` activo.