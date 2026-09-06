# Ticket: PAIML-POLE-ANALYST-074

## Title
[Summary] Plain-language analysis summary (no metric ids / z-scores / frame numbers / deviation counts)

## Description
Phase 25 — see [PLAN_PHASE_25](../plan/PLAN_PHASE_25.md). User-reported defect
from manual staging testing: the analysis summary section renders technician
prose, e.g. "339 deviations detected — most critical: torso_tilt_speed in the
Hold phase (z=-20, frame 316) — overall score 88/100."

Root site: `app/pole_analyst/src/app/features/analysis/models/summary.ts`
composes this string from live data (format hardcoded, values live), and
`summary.spec.ts` (lines ~129-183) codifies the jargon as expected output —
the specs currently assert the technician wording, so they lock the bug in.

Requirement: the summary section renders **human-understandable coach
sentences ONLY**:

- No `snake_case` metric ids — map every metric to a human name
  (e.g. `torso_tilt_speed` → torso control; see mapping table in
  `PLAN_PHASE_25.md`).
- No z-scores (`z=-20`, `|z|`, "deviations", "σ").
- No frame numbers (`frame 316`, "at frame …").
- No raw deviation counts ("339 deviations detected").
- The overall score may stay (`88/100`-style) — it is already human.
- Tone follows phase-22 coach plain language (`PAIML-POLE-ANALYST-071`):
  short supportive coach sentences, named body focus + phase, one
  next-step cue. Never raw JSON / technical dumps.

## What to Do (Implementation Steps)
- [ ] Rewrite the composer in `summary.ts`: keep the live-data inputs
      (`scores`, `detections`, `critical_*`, phases) but replace the
      hardcoded technician template with plain coach sentences built from
      the human-name metric map. Centralize the map (metric id → human
      name) so future metrics reuse it; unknown ids fall back to a generic
      human phrase, never the raw id.
- [ ] Strip all four jargon classes at the composer boundary (metric ids,
      z-scores, frame numbers, deviation counts) — assert none leak via the
      template, pluralization, or tooltip/title strings in this section.
- [ ] Update `summary.spec.ts` (lines ~129-183 and neighbours): replace
      jargon-asserting expectations with plain-sentence assertions
      (human names present, `snake_case`/*z=*/`frame`/counts absent).
      Add cases for: single critical finding, multiple findings, and the
      no-critical-findings (positive) path.
- [ ] Keep the overall score rendering; keep phase names human
      (`Hold`-style, not codes).
- [ ] Add/adjust unit specs to ≥ 80% coverage for the composer + map.

## Before / After Examples (normative)

1. **Critical torso finding (Hold)**
   - Before: "339 deviations detected — most critical: torso_tilt_speed in
     the Hold phase (z=-20, frame 316) — overall score 88/100."
   - After: "Your torso control wobbled during the Hold — overall score
     88/100. Steady your ribs over your hips next rep."

2. **Leg-line finding (Climb)**
   - Before: "112 deviations detected — most critical: knee_extension_angle
     in the Climb phase (z=-3.4, frame 98) — overall score 74/100."
   - After: "Your leg extension faded during the Climb — overall score
     74/100. Press through straight legs to the top."

3. **Grip finding (Invert)**
   - Before: "57 deviations detected — most critical: grip_pull_force in the
     Invert phase (z=2.8, frame 201) — overall score 81/100."
   - After: "Your pull timing slipped during the Invert — overall score
     81/100. Set your grip, then pull smoothly."

4. **Positive path (no critical findings)**
   - Before: "0 deviations detected — overall score 93/100."
   - After: "Clean run — nothing critical to fix. Overall score 93/100.
     Hold this shape and add speed."

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] The summary section renders coach sentences only: no `snake_case`
      metric id, no z-score, no frame number, no raw deviation count in any
      tested state (asserted by specs).
- [ ] Human-name mapping applied (e.g. `torso_tilt_speed` → torso control);
      unknown metric ids never leak raw.
- [ ] Overall score still shown; tone matches phase-22 plain language.
- [ ] `summary.spec.ts` jargon expectations replaced with plain-sentence
      assertions (single / multiple / positive paths).
- [ ] `npx ng test --watch=false` green, `npx ng lint` clean,
      `npx ng build` typecheck passes.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`
- [ ] `npx ng lint`
- [ ] `npx ng build`
- [ ] Manual spot check: analyzed video Summary tab shows the After-style
      sentences (no technician prose).

## Dependencies
- **Blocks**: None.
- **Blocked By**: None. Tone reference: `PAIML-POLE-ANALYST-071` (phase 22).
  Backend-independent (FE-only composer + specs change).

## Estimated Effort
- [M]
