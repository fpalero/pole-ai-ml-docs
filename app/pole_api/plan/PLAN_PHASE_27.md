# Fase 27 — Coach-insights positives (`perfect` bar: score_pct ≥ 70) — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Origen: PO report — the `pole_analyst` "Tips & Insights"
> panel shows only negative (`wrong`/`adjustment`) insights, never positive/`perfect` ones.

## Contexto

`GET /api/analysis/videos/{id}/coach-insights` serves rule-based insights from
`CoachInsightsService` (via `CoachService._rule_insights()`). Its `perfect` classification uses
`PERFECT_Z_THRESHOLD = 0.5` (`coach_insights_service.py` line 43) ⇒ `score_pct ≈ ≥ 75` — stricter
than the requested `score_pct ≥ 70` and inconsistent with `coach_service.py`'s existing LLM-path
override (`score_pct >= 70 → perfect`). The FE pipeline is intact; the backend bar starves it of
`perfect` insights.

USER-CONFIRMED decision (Option A): `perfect` ⟺ `score_pct ≥ 70` ⟺ `|z| ≤ 0.6`, since
`insight_score_pct(z) = 100·(1−|z|/2)`.

## Tickets

| Ticket | Scope | Estado |
| :--- | :--- | :--- |
| `PAIML-POLE-API-083` | Relax rule-based `perfect` threshold to `score_pct ≥ 70` (`\|z\| ≤ 0.6`); docstring + tests | 📋 PLANNED |

## Tasks

- Change `PERFECT_Z_THRESHOLD` `0.5` → `0.6`; update the module docstring (`|z| <= 0.5` → `|z| <= 0.6`).
- Add/adjust unit tests for the newly-`perfect` band (`0.5 < |z| ≤ 0.6`); `adjustment`/`wrong`
  boundaries unchanged.

## Acceptance

- `perfect` produced for `0.5 < |z| ≤ 0.6`; `adjustment`/`wrong` boundaries unchanged;
  `pixi run test-api` green, coverage ≥ 80%.

## Dependencies

- **Blocks:** `pole_analyst` Phase 21 (`PAIML-POLE-ANALYST-070` — FE "What's working" guard; this
  backend change lands first so the FE has positives to render).
- **Blocked By:** None (independent).
