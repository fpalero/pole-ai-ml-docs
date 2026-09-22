# Ticket: PAIML-POLE-API-134

## Title
Readiness tiered answer contract (T1/T2/T3) + RE-02 session-resolution investigation (phase-42 gate iter-3 residual)

- **Status**: 📋 PLANNED
- **Project**: pole_api (readiness flow + analyst graph)
- **Phase**: 42 coach-gate-25
- **Blocks**: —
- **Blocked By**: — independent of 135/136/137 (none block each other).

## Context

Phase-42 gate iteration 3 (final): RED 19/25. Remaining readiness failures:
RE-01/02/03/05 no-metrics; RE-04 tool-selection flake (see 136). Evidence:
transcript
`app/pole_analyst/test-results/coach-150q/sample5-3a335cf-iter3-full-20260921-235109/coach-150q-transcript.jsonl`.

USER DECISIONS (binding): (1) **No mock data** — real performances uploaded via
pole_fe by the user on staging; available tricks: **handspring + Shoulder Mount
only**. (2) Revert ticket 131's fake `seed-measurements` endpoint (code PR #332)
and the DEVOPS-002 staging opt-in (infra PR #39) — see 137 / DEVOPS-003.
(3) **Absence of data is a tested behavior, not a setup failure** — for tricks
without footage the gate asserts the fallback answer (tiers below), never
manufactured metrics.

Readiness bank (exact): RE-01 "Am I ready for Ayesha?", RE-02 "Can I compete
this season with my current handspring?", RE-03 "Are my percentiles high enough
for Aerial Shoulder Mount?", RE-04 "What prerequisites am I missing for the Jade
split?", RE-05 "Am I ready to attempt Brass Monkey on spin?"

## Scope

1. **Implement the user-approved tiered readiness answer contract:**
   - **T1 — direct metrics exist:** full verdict + evidence (metrics, percentiles,
     cohort detail where available).
   - **T2 — no direct metrics but prerequisite metrics exist:** partial
     assessment + RECOMMEND (never gate/block) transition tricks + cite owned
     prerequisites. Recommendation-only language + existing disclaimer/safety
     patterns.
   - **T3 — nothing (no direct, no prerequisite metrics):** structured
     video-request CTA — upload action block, trick-specific guidance,
     ask-once-per-trick, no nag loops.
2. **RE-02 session-resolution investigation:** handspring HAS metrics yet RE-02
   failed — the flow may resolve "my current handspring" to the wrong session.
   Trace free-text → session resolution for RE-02 and fix (prefer most-recent
   scored coached session for the named trick).
3. **Prerequisite source preference (binding):** (1) catalog progression edges
   if they exist — verify via code (tickets 110/113); else (2) RAG retrieval
   over the pole knowledge base. **NO** hand-authored test-only maps, **NO**
   fake metrics.

## Validation Plan
1. Targeted battery:
   ```bash
   npx playwright test coach-150q.spec.ts --workers=1 -g "COACH7-(RE-01|RE-02|RE-03|RE-04|RE-05)"
   ```
2. RE-02 resolves to the handspring session that has metrics (log proof).
3. Tricks without footage return the T2/T3 fallback per mapping below — never
   manufactured metrics.

## Acceptance Criteria
- [ ] T1/T2/T3 contract implemented with recommendation-only language +
      existing disclaimer/safety patterns.
- [ ] Binding per-case mapping: RE-02→T1; RE-03→T1 (percentile/cohort detail
      open); RE-01→T2 iff catalog edges connect Ayesha to owned prerequisites
      (handspring/Shoulder Mount) else T3; RE-05→T2 iff edges connect Brass
      Monkey similarly else T3; RE-04→T2-style + determinism via 136.
- [ ] RE-02 passes against the real handspring session (session-resolution fix
      verified).
- [ ] Prerequisites come from catalog edges (verified present) or RAG
      retrieval — no hand-authored test-only maps, no fake metrics.
- [ ] T3 CTA has upload action block + specific guidance + ask-once-per-trick
      (no nag loops).

## Dependencies
- **Blocked By**: — (catalog 110/113 verification is part of this ticket).
- **Blocks**: —.

## Estimated Effort
- [M]
