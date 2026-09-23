# Ticket: PAIML-POLE-API-141

## Title
RE T2/T3 tier-appropriate spec assertions (test-only recalibration)

- **Status**: 📋 PLANNED
- **Project**: pole_api (gate spec `app/pole_analyst/e2e/coach-150q.spec.ts`)
- **Phase**: 42 coach-gate-25
- **Blocks**: —
- **Blocked By**: — independent of 140 (none block each other).

## Context

Local SAMPLE-5 gate 21/25 (run `20260923-205700`, report
`docs/app/pole_api/phase-42-coach-gate-25/LOCAL_GATE_20260923_2125.md` — binding
evidence). RE-05 fails by design: zero Brass Monkey data exists anywhere, so
the T3 video-request is the CORRECT answer — but the spec's "matrix has data
rows" assertion contradicts the approved tier contract (ticket 134). The app
is right; the spec is wrong. Fix is spec-side, test-only, no production code.

Binding tier contract (from 134): T1 = direct metrics exist (full verdict +
evidence); T2 = prerequisite metrics only (partial assessment +
recommendation-only transition tricks + owned-prerequisite citations); T3 =
nothing (structured video-request CTA: upload action block, trick-specific
guidance, ask-once-per-trick, no nag loops).

## Scope

Test-only changes in `app/pole_analyst/e2e/coach-150q.spec.ts`:

1. **Replace** the blanket "matrix has data rows" assertion with
   tier-shape assertions:
   - **T2:** prerequisite mentions present + recommendation-only copy
     (never gate/block language) + owned-score citations present.
   - **T3:** `readiness_cta` block present + upload `quick_replies` pill
     present + ask-once behavior (second identical ask → one-line reminder,
     not a full CTA re-emission).
2. **Keep T1 assertions unchanged** (matrix rows + `rag_proof`).

Out of scope: production code; tier semantics (134 owns those); touching
PR/VA/TP/IN assertions.

## Validation Plan

1. Targeted battery on a stack serving 134+ tiers (local k3s or staging):
   ```bash
   npx playwright test coach-150q.spec.ts --workers=1 -g "COACH7-(RE-01|RE-04|RE-05)"
   ```
   (RE-01 exercises T2-or-T3 path per 134 mapping, RE-04 T2-style, RE-05 T3.)
2. Full RE battery (`RE-01`–`RE-05`) green on the same stack.
3. Negative check: T1 cases still assert matrix rows + `rag_proof` (unchanged).

## Acceptance Criteria

- [ ] RE-01 / RE-04 / RE-05 assert tier shapes (not "matrix has data rows").
- [ ] T1 assertions (matrix rows + `rag_proof`) unchanged.
- [ ] Full RE battery green on a stack serving 134+ tiers (local k3s or
      staging).
- [ ] No production-code change in this ticket.

## Dependencies

- **Blocked By**: — (requires a stack serving 134+ tiers to validate, but
  that is environment, not a ticket dependency).
- **Blocks**: —.

## Estimated Effort

- [S] (spec-only assertion swap + battery runs)
