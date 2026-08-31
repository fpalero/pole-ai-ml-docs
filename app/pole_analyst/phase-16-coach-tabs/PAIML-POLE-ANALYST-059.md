# Ticket: PAIML-POLE-ANALYST-059

## Title
[Features] SummaryTab / PlanTab / PoseTab render structured coach content (+ legacy fallback)

## Description
Phase 16 Phase B (PLAN_PHASE_16.md). Wire the coach payloads (PAIML-POLE-ANALYST-058) into the
three tabs. PlanTab switches to structured-first rendering and keeps the existing
`models/plan.ts` markdown parser as fallback for sessions without a persisted coach plan.

Rendering:
- **SummaryTab**: "Critical insight" card + "Next session focus" directive below the metric cards;
  skeleton while generating; 503 → inline retry affordance.
- **PlanTab**: four week-cards (`week`, `focus`, `drills[]`) + "The Issue" header +
  `bail_strategy` safety card (distinct warning styling); fallback to legacy parse when no payload.
- **PoseTab**: `action_step` as primary CTA; flaw/correction/aesthetic feedback as secondary
  callouts alongside current detection hints.

## What to Do (Implementation Steps)
- [ ] SummaryTab / PlanTab / PoseTab consume `AnalysisService` coach methods via
      `takeUntilDestroyed` patterns (no subscription leaks).
- [ ] PlanTab dual-source logic: structured payload first, legacy agent_reply parser second.
- [ ] Loading skeletons during generation; typed error states (404/409/503).
- [ ] Unit tests per tab component; extend Playwright E2E for the coach flows against the
      mocked-LLM backend (`pixi run api`, `_testing` DBs).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] All three tabs render structured coach content with fallbacks.
- [ ] No subscription leaks; lint + typecheck green.
- [ ] E2E covers summary insight card, plan weeks rendering, pose action step.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`
- [ ] `npx playwright test` (pole_analyst suite, mocked backend)

## Dependencies
- **Blocks**: none
- **Blocked By**: PAIML-POLE-ANALYST-058

## Estimated Effort
- [M]
