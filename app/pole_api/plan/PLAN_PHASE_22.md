# Fase 22 — Coach insights (rule-based z-score insights + pose extraction + fps storage) — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Tickets: PAIML-POLE-API-065..069
> (renumerados desde 064..068 para resolver la colisión con Phase 21)

## Contexto

Backend support for coach-facing summary content: store video `fps` at upload time, extract pose
frames lazily on first access, classify threshold-based frame insights (✅/⚠️/❌) persisted on the
video doc, expose them via endpoint + chatbot tool, and integrate into the analysis worker.

> NOTE: this plan file was reconstructed after the parallel session left only ticket files; it
> lists the existing tickets verbatim. See each ticket for full detail.

## Tickets

| Ticket | Title |
| :--- | :--- |
| [PAIML-POLE-API-065](../phase-22-coach-insights/PAIML-POLE-API-065.md) | [Infrastructure] Store fps on video doc at upload time |
| [PAIML-POLE-API-066](../phase-22-coach-insights/PAIML-POLE-API-066.md) | [Infrastructure] Lazy pose frame extraction on first /pose/frames access |
| [PAIML-POLE-API-067](../phase-22-coach-insights/PAIML-POLE-API-067.md) | [Application] CoachInsightsService — threshold-based frame classification + persistence |
| [PAIML-POLE-API-068](../phase-22-coach-insights/PAIML-POLE-API-068.md) | [Application] Coach insights endpoint + chatbot tool |
| [PAIML-POLE-API-069](../phase-22-coach-insights/PAIML-POLE-API-069.md) | [Pipeline] Integrate coach insights into analysis worker |

Dependency chain (per tickets): 065 → {066, 070}; 066 → {070}; 067 → {068, 069};
068 → {069}; 069 → {070, 071}. Phase 23 tickets: 070 (Summary tab UI), 071 (notification + chat).

## Quality Gates

- **Integration Tests:** `pixi run test-api` (guarded `_testing` DBs).
- **Coverage Requirement:** ≥ 80%.
