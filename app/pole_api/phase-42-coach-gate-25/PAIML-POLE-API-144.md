# Ticket: PAIML-POLE-API-144

## Title
Finish 143's tier-marker emission on ReAct-delegated readiness paths (RE-01/RE-04)

- **Status**: 📋 PLANNED
- **Project**: pole_api (analyst readiness shaping — ReAct-delegated path)
- **Phase**: 42 coach-gate-25
- **Blocks**: —
- **Blocked By**: — independent (implement sequentially with 145 only to avoid shared-file conflicts, not a ticket dependency).

## Context

Latest local gate run on develop `7ed367f` (142+143 live) — run log
`/tmp/coach-full-7ed.log`, **21/25**. Binding evidence, written faithfully:

- Per-flow: video_analysis 5/5, progress 4/5 (PR-04), training_plan 4/5
  (TP-02), injury 5/5, readiness 3/5 (RE-01, RE-04, RE-05).
- 142 PROVEN (zero blank-turn deaths — the `[],[],[]` epidemic is gone).
- 143 routing PROVEN (clarification detour gone — PR-01/02/03/05 pass).

Residual failures, three kinds:

1. PR-04 / TP-02: `strict mode violation:
   locator('.bubble-assistant').last().locator('.matrix-card') resolved to 2
   elements` (Handspring Progress Matrix + Session comparison) and
   `.drills-list` resolved to 3 elements — answers are now RICHER (two
   matrices / three drill groups), the spec locator assumes exactly one. NOT
   a product regression.
2. RE-01 / RE-04: 143's tier-marker emission still not firing on these
   delegated paths — RE-04 transcript `blocks: [md]`, 3 RAG calls
   (query_pole/biomechanics/calisthenics), rag False, classified T1 but
   should be T2. 143's routing half works; the marker-emission half has a
   residual gap on these two turns.
3. RE-05: `Error reading storage state .../.auth/state.json` (auth file wiped
   mid-run race — recurring); GATE: tallied `video_analysis 0/5` despite all
   5 VA passing (per-test transcript isolation empties the tally source).

Prior tickets cover: 134 tiers (T1/T2/T3 contract), 135 blank-retry, 136
deterministic readiness retrieval, 140 md-first, 141 tier asserts, 142 blank
forensics, 143 answer-shape alignment + PR-02 routing.

This ticket owns residual kind (2). Kinds (1) and (3) belong to 145
(spec/harness hardening, test-only).

## Scope

1. **Trace** why `ensure_readiness_tier_answer` /
   `_apply_react_tier_shaping` doesn't emit T2 markers for RE-01/RE-04 —
   RE-04 answer has real RAG hits + owned-prereq data but emits only `[md]`.
2. **Fix** so the delegated (ReAct) path emits 134's T2/T3 markers
   byte-identically (same header text, same placement as the terminal
   shaping path).

Constraints (hard-stops):

- Markers from single source of truth (`readiness_tiers`) — no duplicated
  marker strings.
- No fabrication: markers only on grounded answers (real retrieval hits /
  owned-prereq data, as RE-04 already has).
- Owner/athlete scoping on any new retrieval (prefer none — reuse the
  existing 3 RAG calls / owned-prereq data).
- Recommendation-only (no training-plan mutation, no medical claims).
- 125/134/135/136/140/143 suites green.

Out of scope: spec/harness changes (145 owns those); blank-retry paths (142
owns those); md-first shaping (140 owns that); PR-04/TP-02 locators, auth
race, GATE tally (all 145).

## Validation Plan

1. Hermetic replay of RE-01/RE-04 delegated turns: answer carries 134's
   T2 (or T3) markers byte-identically to the terminal path.
2. Repeated hermetic runs: classification stable at T2 (or T3), markers
   present every run (no flake).
3. Regression: 125/134/135/136/140/143 suites green; T1 assertions
   untouched.
4. Live battery proof deferred to gate time (staging down, local k3s holds
   current images):
   `npx playwright test coach-150q.spec.ts --workers=1 -g "COACH7-(RE-01|RE-04)"`.

## Acceptance Criteria

- [ ] RE-01/RE-04 classified T2 (or T3) with markers present across repeated
      hermetic runs.
- [ ] Delegated-path markers byte-identical to 134's terminal-path markers
      (single source of truth, no fabrication).
- [ ] 125/134/135/136/140/143 suites green; T1 assertions untouched.
- [ ] Live battery proof deferred to gate time (staging down, local k3s holds
      current images) — recorded, not skipped silently.

## Dependencies

- **Blocked By**: — (implement sequentially with 145 only to avoid
  shared-file conflicts, not a ticket dependency; requires a stack serving
  134+ tiers to live-validate, but that is environment, not a ticket
  dependency).
- **Blocks**: —.

## Estimated Effort

- [S] (trace + delegated-path marker fix + hermetic assertions)
