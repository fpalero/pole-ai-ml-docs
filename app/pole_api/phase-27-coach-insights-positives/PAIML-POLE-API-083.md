# Ticket: PAIML-POLE-API-083

## Title
[Analysis] CoachInsightsService — relax rule-based `perfect` bar to `score_pct ≥ 70` (`|z| ≤ 0.6`)

## Description
Phase 27. The `pole_analyst` "Tips & Insights" panel shows only negative insights (wrong/adjustment)
and never positive ("What's working") ones. Verified diagnosis: the frontend pipeline is intact
(`TipsInsightsPanelComponent` renders "Issues" + "What's working"; analysis-tab composes
`allInsights = [...wrong, ...adjustment, ...perfect]`; `api.models.ts` types `perfect`), and the
root cause is the backend rule-based classification in
`app/pole_api/src/analysis/services/coach_insights_service.py`: `PERFECT_Z_THRESHOLD = 0.5`
equates to `score_pct ≥ 75` (via `insight_score_pct(z) = 100·(1−|z|/2)`), a stricter bar than
requested, so `perfect` is often empty on real data.

**Decision (confirmed by user):** relax the rule-based bar to `score_pct ≥ 70` (i.e. `|z| ≤ 0.6`)
→ `perfect`. This aligns the rule-based path — the one actually served by
`GET /api/analysis/videos/{video_id}/coach-insights` (`controllers/videos.py:305-351`) — with the
LLM path in `coach_service.py`, which already applies `score_pct >= 70 → perfect` overrides
(lines 340-360, 559-561, 595-606).

**Alternatives considered:**
- Keep `≥ 75` — rejected: contradicts the LLM-path contract and the confirmed user decision;
  positives stay empty on real data.
- Lower further (e.g. `≥ 60`) — rejected: inflates positives and diverges from the LLM path;
  revisit only with real-data evidence.

## What to Do (Implementation Steps)
- [ ] Relax `PERFECT_Z_THRESHOLD` (`0.5` → `0.6`) / `classify_z` in `coach_insights_service.py` so
  `|z| ≤ 0.6` → **perfect**, `0.6 < |z| ≤ 2` → **adjustment**, `|z| > 2` → **wrong**.
- [ ] Keep `insight_score_pct(z) = 100·(1−|z|/2)` unchanged; verify the boundary maps exactly
  (`|z| = 0.6` ↔ `score_pct = 70`).
- [ ] Add/adjust unit tests in the `coach_insights_service` tests: boundary `|z| = 0.6` → perfect,
  `|z| = 0.61` → adjustment, `score_pct = 70` → perfect, just-below-70 → adjustment; `perfect`
  non-empty on a realistic fixture.
- [ ] Confirm the served endpoint (`GET .../coach-insights`) returns the relaxed `perfect` list
  (no endpoint change expected).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `classify_z` returns `perfect` for `|z| ≤ 0.6`, and the `score_pct ≥ 70 ↔ perfect` parity with
  the LLM path holds.
- [ ] Rule-based `perfect` is non-empty on realistic data where frame scores clear 70.
- [ ] Unit tests pass for boundary + mapping + persistence/get-or-compute paths.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-070 (frontend "What's working" guard)
- **Blocked By**: None (threshold-only change inside the existing service)

## Estimated Effort
- [S]
