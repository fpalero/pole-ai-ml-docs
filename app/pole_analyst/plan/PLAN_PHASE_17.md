# Fase 17 — Stitch detail views (nueva pantalla "Analysis Details" + Filter Modal) — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Diseño: Stitch "Pole AI Coach", pantallas
> *Analysis Details – Fully Interactive Technical Views* y *Persistent Chat – Video Library
> Filter Modal* (añadidas 2026-08-23)

## Contexto

The newly added Stitch screens specify the target visuals for the analysis detail page and add a
library filter modal. Coverage as of 2026-08-23:

- **Already implemented** (Phases 12–16 + PRs #100–#111): sidebar, tabs
  Summary/Histogram/Pose/Plan, metric cards, AI Insights ✅/⚠️/❌ cards, detected-error card,
  phase durations bar, notification banner, history table, structured coach tabs.
- **Gaps planned here:** library **Filter Modal**; **Metric Distribution Analysis** cards with
  session deltas (`+12% vs last session`, `Peak Performance`); and a **parity pass** aligning the
  detail page with the screen (Overall Score card in header, correction-drill CTA linking insights
  → Plan drills, objectives/drills layout on the Plan tab, `Histogram` tab label → `Statistics`,
  Pose Insights correct/needs-adjustment lists).

## Alcance

### 1. Video Library Filter Modal (`PAIML-POLE-ANALYST-060`)
Standalone modal opened from the library pane's toolbar: filters by trick label, analyzed status,
date range; composes with the existing client-side search; accessible focus trap, dismissible.

### 2. Metric Distribution Analysis (`PAIML-POLE-ANALYST-061`)
SummaryTab section consuming `GET .../metric-deltas` (pole_api Phase 24): per-metric cards with
current value, delta badge (`+12% vs last session`, green/red), `Peak Performance` flag; hidden
when no baseline exists.

### 3. Detail-page parity pass (`PAIML-POLE-ANALYST-062`)
- Header Overall Score card reusing the existing FE-derived score (`summary.ts::pickOverallScore`).
- Insights warning cards gain `View Correction Drill` CTA anchoring to the matching drill on the
  Plan tab.
- PlanTab renders design layout: numbered Core Objectives block + Recommended Drills grid
  (mapper accepts coach-plan JSON; weeks rendered as objective groups when present).
- Tab label `Histogram` → `Statistics`; PoseTab insights lists styled as What's Correct /
  Needs Adjustment per screen.

## Implementation Roadmap

### Phase A: Filter modal (-060)
- [ ] Component + unit specs; compose with search bar.

### Phase B: Distribution cards (-061)
- [ ] Service method + mappers for metric-deltas payload; SummaryTab section; hidden-empty behavior.

### Phase C: Parity pass (-062)
- [ ] Score card, CTA anchor scroll, PlanTab layout, label/style tweaks; visual review vs screen.

## Quality Gates

- **Unit Tests:** `pixi run test-analyst` — ≥ 80% coverage en `src/app`.
- **E2E:** Playwright contra backend `_testing` con LLM mockeado.
- **Additional Checks:** lint/typecheck (`ng build`), sin subscription leaks.

## Dependencies

- **Blocked By:** `-061` ← PAIML-POLE-API-072; `-060`/`-062` sin bloqueos de backend nuevos
  (insights y coach tabs ya mergeados en #100–#111).
- **Blocks:** none.

## Open Questions

- ¿Renombrar también rutas/selectores E2E existentes al renombrar la pestaña a `Statistics`?
  Decidir en -062 (riesgo bajo, actualizar specs).
