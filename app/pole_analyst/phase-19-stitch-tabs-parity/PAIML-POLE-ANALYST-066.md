# Ticket: PAIML-POLE-ANALYST-066

## Title
[Features] Plan tab auto-generates for the detected trick — no manual entry when trick known

## Description
Phase 19 (PLAN_PHASE_19.md). When the analysed video has a detected `trick_label`, the Plan tab
must show the improvement plan for that trick automatically (POST /coach-plan is
generate-or-return-cached keyed by target_trick — first visit may take seconds: show loading
skeleton). Manual target-trick input remains ONLY for videos without a detected label. Write-through
to CoachPlanCacheService stays (CTA flow from -062 depends on it).

## What to Do (Implementation Steps)
- [ ] On PlanTab init (loaded state, video analyzed): if detected `trick_label` present and no cached
      plan → auto-call generatePlan(trick_label) once (guard against duplicate calls across remounts
      via cache/service marker); skeleton while generating.
- [ ] Hide the manual input row when auto path used; keep input + generate button when no
      trick_label (fallback unchanged).
- [ ] Error degradation: generation failure shows inline retry affordance, never blocks other tabs.
- [ ] Specs: auto-path (detected label), fallback path (no label), no-duplicate-generation guard,
      cache write-through, CTA anchor flow still green.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Analyzed video w/ detected trick → plan visible without any user input.
- [ ] No trick detected → previous manual flow intact.
- [ ] Suite green; build clean.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`

## Dependencies
- **Blocks**: none · **Blocked By**: none
- Effort: [M]
