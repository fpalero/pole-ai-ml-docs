# Fase 24 — Stitch detail gaps BE (session-over-session deltas) — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Diseño: Stitch "Pole AI Coach" → pantalla
> *Analysis Details – Fully Interactive Technical Views* (añadida 2026-08-23)

## Contexto

The new Stitch analysis-details screen shows **Metric Distribution Analysis** cards with
session-over-session context: `+12% vs last session`, `Peak Performance`. The backend has no
notion of previous analyses for comparison — each video doc stands alone. Everything else on that
screen is covered by Phases 20–23 (insights cards, durations bar, coach endpoints) or existing
data (`overall_score` already derived FE-side via `summary.ts::pickOverallScore`; history list
exposes it since Phase 20).

This is the **only BE change** required by the new screens; the rest of the Stitch work is FE-only
(`pole_analyst` Phase 17).

## Alcance

### Session-over-session metric comparison

New endpoint returning per-metric deltas between the target video's scored histogram and the most
recent **prior** analyzed video (same trick label preferred):

```
GET /api/analysis/videos/{video_id}/metric-deltas
→ { baseline_video_id, metrics: [{ key, current, previous, delta_pct, improved }],
    peak_flags: [{ key }] }
```

- Baseline rule: same `trick_label`, latest `analyzed_at <` current; documented at ticket level.
- `delta_pct` computed on shared metric keys only; missing keys omitted (never invented).
- `peak_flags`: metrics whose current value is the max across ALL analyzed videos for that trick
  ("Peak Performance" badge).

## Endpoints

| Endpoint | Método | Descripción | Nuevo |
| :--- | :--- | :--- | :--- |
| `/api/analysis/videos/{id}/metric-deltas` | GET | Deltas vs last comparable session + peak flags | **Nuevo** |

## Implementation Roadmap

### Phase A (ticket PAIML-POLE-API-072)
- [ ] Repo lookup for baseline video (indexed query on `trick_label` + `analyzed_at`).
- [ ] Pure delta service over two scored histograms + peak-flag aggregation.
- [ ] Endpoint + Pydantic DTOs + integration tests.

## Quality Gates

- **Integration Tests:** `pixi run test-api` (guarded `_testing` DBs).
- **Coverage Requirement:** ≥ 80%.

## Dependencies

- **Blocks:** PAIML-POLE-ANALYST-061 (FE distribution cards).
- **Blocked By:** none (Phase 22 insights already merged).

## Open Questions

- Same-trick-only vs any prior video when no same-trick history exists? Default: return empty
  metrics (FE hides the card rather than showing misleading deltas) — confirm at ticket.
