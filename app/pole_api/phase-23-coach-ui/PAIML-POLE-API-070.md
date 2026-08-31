# Ticket: PAIML-POLE-API-070

## Title
[Frontend] Summary tab enhancement — CoachInsights cards + DetectedError card + PhaseDurations bar

## Description
Phase 23 (§1). Enhance the Summary tab in `analysis-detail.page.ts` with three new components:

1. **CoachInsightsCard** — renders structured ✅/⚠️/❌ insight cards from
   `GET /coach-insights`. Groups by phase, shows metric name, z-score, and explanation.
2. **DetectedErrorCard** — renders the top wrong insight (|z| > 2) as a dedicated error card
   with frame link and correction hint.
3. **PhaseDurationsBar** — time-based durations (`Entry X.Xs · Hold X.Xs · Exit X.Xs`) using
   stored fps and phase frame bounds.

Keep existing phase timeline alongside (Q7B).

## What to Do (Implementation Steps)
- [ ] Create `CoachInsightsCardComponent` (inline template/styles, standalone).
  - Input: `insights` signal from `/coach-insights` API.
  - Render: grouped by phase, each insight shows icon (✅/⚠️/❌), metric, z-score, explanation.
- [ ] Create `DetectedErrorCardComponent` (standalone).
  - Input: top wrong insight from coach insights.
  - Render: red card with frame number, metric, z-score, explanation, "View in Pose tab" link.
- [ ] Create `PhaseDurationsBarComponent` (standalone).
  - Input: `phases` + `fps` from video summary.
  - Render: horizontal bar with phase labels and time durations.
- [ ] Wire all three into `SummaryTabComponent` — fetch `/coach-insights` on init, render cards.
- [ ] Update `AnalysisService` with `getCoachInsights(videoId)` method.
- [ ] Unit tests for each new component.
- [ ] FE tests: `pixi run test-analyst`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Summary tab shows CoachInsights cards with ✅/⚠️/❌ icons.
- [ ] DetectedError card shows top wrong insight with frame link.
- [ ] PhaseDurationsBar shows time-based durations alongside existing timeline.
- [ ] All components are standalone with inline template/styles.
- [ ] Unit tests pass for all new components.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-analyst` (FE test suite).

## Dependencies
- **Blocks**: None
- **Blocked By**: PAIML-POLE-API-065 (fps), PAIML-POLE-API-066 (pose frames), PAIML-POLE-API-068 (coach-insights endpoint)

## Estimated Effort
- [L]
