# Ticket: PAIML-POLE-API-131

## Title
Readiness seed state missing measurements (Class C): seed session measurements so retrieval-with-hits preconditions hold (RE-01, RE-02, RE-03, RE-05)

## Status
📋 PLANNED — follow-up gate-fix ticket for phase-42 coach-gate-25, SAMPLE-5 gate
run `sample5-647d57e-20260921-205203` (**15/25, RED**).

- **Status**: 📋 PLANNED
- **Project**: pole_api (seed/coach flow + e2e harness)
- **Phase**: 42 coach-gate-25
- **Blocks**: —
- **Blocked By**: — independent of 129/130/132 (none of the four gate-fix
  tickets block each other).

## Context

SAMPLE-5 gate run `app/pole_analyst/test-results/coach-150q/sample5-647d57e-20260921-205203/`
(`coach-150q-judge.md` + `coach-150q-transcript.jsonl`): **COACH7-RE-01, RE-02,
RE-03, RE-05 fail** `retrieval-with-hits Expected true Received false` at
`coach-150q.spec.ts:597`; the analyst answers "No metrics are available for
this session, so readiness cannot be evaluated yet." (judge rows: fail,
`rag_proof` false, blocks `md` only). RE-04 already passes and **must stay
green**.

### Evidence / root cause
The seeded mirror video for the coached session used by the readiness flow
extracted **0 frames**
(`Completed skeleton extraction: processed 0 frames ... e2e_coach_150q...mp4`)
→ the session has **no measurements** → the analyst truthfully reports no
metrics — but spec:597 expects RAG hits (retrieval-derived evidence) for the
readiness flow, which structurally requires session metrics.

This is a **seed-state defect**, not an analyst bug: the reply is truthful;
the seed produced no retrievable data to ground the readiness answer.

## Scope (Option A, CHOSEN)

Seed session **measurements** for the coached session used by the readiness
flow so the retrieval-with-hits preconditions are met:

- fix the seed source: replace / repair the mirror fixture so skeleton
  extraction yields **≥ 1 frame**, or
- seed measurements **directly at the session level** via the same mechanism
  the app uses.

**Do NOT** relax spec:597 if metrics genuinely exist for the session — only
calibrate the spec to accept the truthful no-metrics reply when a session
**legitimately has none** (and document which session that is).

## Files Affected
- Seed fixture / mirror video used by the coached readiness session
  (COACH7-SETUP or equivalent; the `e2e_coach_150q...mp4` source).
- Possibly the readiness flow's measurement seeding path
  (`pole_coach` readiness / `analyst_chatbot` session seeding).
- `app/pole_analyst/e2e/coach-150q.spec.ts:597` — only if a session is
  documented as legitimately metrics-free.

## Validation Plan
1. Readiness battery:
   ```bash
   npx playwright test coach-150q.spec.ts --workers=1 -g "COACH7-(RE-01|RE-02|RE-03|RE-04|RE-05)"
   ```
   RE-01/02/03/05 must pass with `rag_proof` true; **RE-04 already passes and
   must stay green**.
2. Skeleton extraction log shows **frames > 0** for the seeded mirror fixture
   (or measurements seeded at session level).
3. Full SAMPLE-5 gate **25/25** as phase acceptance (with 129/130/132).

## Acceptance Criteria
- [ ] RE-01, RE-02, RE-03, RE-05 pass in the SAMPLE-5 gate with `rag_proof`
      true.
- [ ] RE-04 stays green (no regression).
- [ ] Seed produces ≥ 1 frame for the readiness mirror fixture, or session
      measurements are seeded via the app's own mechanism.
- [ ] Any session that legitimately has no metrics is documented; only then may
      spec:597 accept the truthful no-metrics reply.

## Dependencies
- **Blocked By**: —.
- **Blocks**: — (independent of 129/130/132).

## Estimated Effort
- [M]