# Ticket: PAIML-POLE-API-146

## Title
RE-04 Jade T2 citations: guard-trip forensics + fix delegated retrieval (owned/prereq arrays)

- **Status**: 📋 PLANNED
- **Project**: pole_api (analyst readiness — retrieval + T2 shaping)
- **Phase**: 43 staging-gate-residuals
- **Blocks**: —
- **Blocked By**: —

## Context

Staging SAMPLE-5 gate RUN_ID `20260924-163713` scored **22/25**: VA 4/5
(VA-05 timeout), RE 3/5 (RE-04 T2-citations + RE-05 missing-CTA).
RE-01/RE-03 were fixed by 144 (delegated tier-marker emission); this ticket
owns the RE-04 residual.

Binding evidence, written faithfully:

- Question: "What prerequisites am I missing for the Jade split?" expects
  `md` + `retrieval_hits`.
- RE-04 transcript: `blocks: [md]`, shaped-untouched or empty-prereq —
  `get_readiness_prerequisites` either never fired or fired with empty
  owned/prereq arrays, so the T2 citation shape never materialized despite
  real RAG calls on the turn.
- Suspect legs (two candidates, forensics decides):
  (a) 136-backstop guards in `coach_providers.py:793-856` returning `[]`
  (owner-scope guard `810-811` prime suspect); (b) T2 shaping early-return
  in `answer_shaping.py:1604-1640` (`ensure_readiness_tier_answer` T2 branch)
  leaving shaped-untouched.
- Staging logs show `supergraph invoke exceeded 30.0s budget; delegating`
  every turn — delegated (ReAct) path is the live path for this turn.
- Artifacts: `app/pole_analyst/test-results/coach-150q/20260924-163713/`.
- RAG ref: `pixi run docs-rag-read "coach-150q SAMPLE-5 25 questions gate" --k 5`.
- ADR: `docs/decisions/ADR-006-readiness-overall-score-gate-precondition.md`.

Prior tickets cover: 134 tiers (T1/T2/T3), 136 deterministic retrieval,
141 tier asserts, 143/144 delegated marker emission, 145 spec/harness.

## Scope

1. **Forensics** — determine which guard returns `[]`/shaped-untouched on
   Jade turns: instrument the 136-backstop guards
   (`coach_providers.py:793-856`, incl. owner-scope guard `810-811`) vs the
   T2 shaping early-return (`answer_shaping.py:1604-1640`); add guard-trip
   debug logging/counters (which leg tripped, with owned/prereq sizes).
2. **Fix** the tripped leg so `get_readiness_prerequisites` fires with
   owned/prereq arrays populated — or record, with evidence, why RAG-only
   T2 is the intended shape for this turn (then adjust the assertion, not
   the code).

Constraints (hard-stops):

- No fabrication: citations only from real retrieval hits / owned-prereq data.
- Owner/athlete scoping preserved on any new retrieval.
- Recommendation-only (no training-plan mutation, no medical claims).
- Single source of truth for T2 markers (`readiness_tiers`) — no duplicated strings.
- 125/134/135/136/140/141/144 suites green.

Out of scope: T3 CTA emission (147 owns that); timeout/latency handling
(148 owns that); spec/harness changes (145 pattern, test-only precedent).

## Validation Plan

1. Hermetic replay of the Jade-split T2 turn: answer carries `md` +
   `retrieval_hits` with owned/prereq citations across repeated runs.
2. Guard-trip logs/counters assert which leg fired (no silent `[]`).
3. Regression: 125/134/135/136/140/141/144 suites green; T1 untouched.
4. Live battery proof deferred to gate time:
   `npx playwright test coach-150q.spec.ts --workers=1 -g "COACH7-RE-04"`.

## Acceptance Criteria

- [ ] Jade-split Q ("What prerequisites am I missing for the Jade split?")
      returns `md` + `retrieval_hits` across repeated hermetic runs.
- [ ] Tripped guard identified, logged/counted, fixed (or RAG-only T2
      intent recorded with evidence).
- [ ] `get_readiness_prerequisites` fires with owned/prereq arrays populated
      (or intent-record exception above applies).
- [ ] 125/134/135/136/140/141/144 suites green; T1 assertions untouched.
- [ ] Live battery proof deferred to gate time — recorded, not skipped silently.

## Dependencies

- **Blocked By**: — (independent of 147/148; implement sequentially only to
  avoid shared-file conflicts in `answer_shaping.py` / `coach_providers.py`,
  not a ticket dependency; requires a stack serving 134+ tiers to
  live-validate, but that is environment, not a ticket dependency).
- **Blocks**: —.

## Estimated Effort

- [S] (guard-trip forensics + delegated-retrieval fix + hermetic assertions)
