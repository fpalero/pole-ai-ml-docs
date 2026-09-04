# Fase 21 — Coach-insights positives ("What's working" guard) — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Origen: PO report — the "Tips & Insights" panel shows only
> negative insights, never the "What's working" positives. Backend root cause fixed in
> `pole_api` Phase 27 (`PAIML-POLE-API-083`).

## Contexto

The FE display + mapping pipeline is intact and unit-tested
(`tips-insights-panel.component.ts`, `analysis-tab.component.ts` `allInsights`,
`coach-insights.ts::insightsViewFrom`), but with the backend bar too strict (`score_pct ≈ ≥ 75`)
no `perfect` insights ever arrived. Once the backend relaxes to `score_pct ≥ 70` (`|z| ≤ 0.6`),
this phase guards the FE so the "What's working" section surfaces positive/`perfect` insights
**only when `score_pct ≥ 70`**.

## Tickets

| Ticket | Scope | Estado |
| :--- | :--- | :--- |
| `PAIML-POLE-ANALYST-070` | Guard "What's working" to `score_pct ≥ 70` positives; unit test; negatives untouched | 📋 PLANNED |

## Tasks

- Confirm `TipsInsightsPanelComponent` renders "What's working" when positives exist (`allInsights`
  includes `perfect`; `insightsViewFrom` maps all groups).
- Guard the positives path to `score_pct ≥ 70` only; do NOT change negative-insight thresholds.
- Add/adjust unit test: empty/missing `perfect` → no section; `score_pct ≥ 70` inputs → section shown.

## Acceptance

- "What's working" shows only `score_pct ≥ 70` positives; negative cards unchanged; FE tests green.

## Dependencies

- **Blocks:** None.
- **Blocked By:** `PAIML-POLE-API-083` (`pole_api` Phase 27 — backend must relax the bar first so
  the FE has positives to render).
