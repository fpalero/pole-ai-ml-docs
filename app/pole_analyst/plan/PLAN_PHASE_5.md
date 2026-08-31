# Fase 5 — Edge / Error / Reconnect hardening — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md)

## Tareas

- [ ] Presentation invalid upload (no `.mp4`, demasiado grande) → inline error + guía "choose another / shorter video".
- [ ] Presentation estado no-detectable-skeleton → mensaje de error del chatbot con causa probable ("low quality, re-record").
- [ ] Infra WS reconnect mantiene `session_id`; placeholders "analysis in progress" sincronizados con `ChatState.Working`.
- [ ] Test unit tests T5.x (error branches, reconnect idempotency).

## Criterios de aceptación

- [ ] Edge cases cubiertos; tests T5.x verdes (UC-05/06).