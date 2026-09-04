# Ticket: PAIML-POLE-ANALYST-070

## Title
[Analysis] Tips & Insights "What's working" — surface positives with `score_pct ≥ 70` guard

## Description
Phase 21 (sister ticket to PAIML-POLE-API-083 — same cross-cutting feature). Once the backend
relaxes the rule-based `perfect` bar to `score_pct ≥ 70`, the endpoint returns non-empty `perfect`
lists; this ticket verifies/guards the frontend so those positives actually render in the "Tips &
Insights" panel's "What's working" section.

Verified intact pipeline (do not rebuild): `TipsInsightsPanelComponent` renders "Issues" +
"What's working"; the analysis tab composes `allInsights = [...wrong, ...adjustment, ...perfect]`;
`api.models.ts` types `perfect`.

## What to Do (Implementation Steps)
- [ ] Verify the `coach-insights.ts` mapper passes `perfect` through to the panel input unchanged.
- [ ] Guard the "What's working" list so it renders positives with `score_pct ≥ 70` (filter at the
  panel or mapper level per repo convention; no new data fetching).
- [ ] Keep the empty state sane: when `perfect` is empty, the section stays hidden (or existing
  neutral copy — follow the component's current convention, do not invent new UX).
- [ ] Adjust/add unit coverage in `tips-insights-panel.component.spec.ts` and/or the
  `coach-insights` mapper spec: positives with `score_pct ≥ 70` render; below-70 items never appear
  under "What's working"; empty `perfect` keeps the section hidden/neutral.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] "What's working" renders backend `perfect` insights with `score_pct ≥ 70`.
- [ ] Items below 70 do not leak into the positives list.
- [ ] Empty `perfect` degrades gracefully per the existing component convention.
- [ ] Unit specs cover render/guard/empty-state cases.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`

## Dependencies
- **Blocks**: None
- **Blocked By**: PAIML-POLE-API-083 (needs non-empty backend `perfect` to verify against;
  mapper/panel work can start in parallel with mocked payloads)

## Estimated Effort
- [S]
