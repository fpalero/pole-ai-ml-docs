# Ticket: PAIML-POLE-API-145

## Title
Spec/harness hardening: multi-element locators, auth-race, GATE tally (test-only)

- **Status**: 📋 PLANNED
- **Project**: pole_api (gate spec + harness — `app/pole_analyst/e2e/coach-150q.spec.ts` + helpers)
- **Phase**: 42 coach-gate-25
- **Blocks**: —
- **Blocked By**: — independent (implement sequentially with 144 only to avoid shared-file conflicts, not a ticket dependency).

## Context

Latest local gate run on develop `7ed367f` (142+143 live) — run log
`/tmp/coach-full-7ed.log`, **21/25**. Binding evidence, written faithfully:

- Per-flow: video_analysis 5/5, progress 4/5 (PR-04), training_plan 4/5
  (TP-02), injury 5/5, readiness 3/5 (RE-01, RE-04, RE-05).
- 142 PROVEN (zero blank-turn deaths — the `[],[],[]` epidemic is gone).
- 143 routing PROVEN (clarification detour gone — PR-01/02/03/05 pass).

Residual failures, three kinds (this ticket owns kinds 1 + 3):

1. PR-04 / TP-02: `strict mode violation:
   locator('.bubble-assistant').last().locator('.matrix-card') resolved to 2
   elements` (Handspring Progress Matrix + Session comparison) and
   `.drills-list` resolved to 3 elements — answers are now RICHER (two
   matrices / three drill groups), the spec locator assumes exactly one. NOT
   a product regression.
2. RE-01 / RE-04 tier-marker gap — owned by 144, not this ticket.
3. RE-05: `Error reading storage state .../.auth/state.json` (auth file wiped
   mid-run race — recurring); GATE: tallied `video_analysis 0/5` despite all
   5 VA passing (per-test transcript isolation empties the tally source).

Prior tickets cover: 134 tiers, 135 blank-retry, 136 determinism, 140
md-first, 141 tier asserts (test-only precedent), 142 blank forensics, 143
answer-shape alignment + PR-02 routing, 144 delegated tier markers.

## Scope

Test-only — `app/pole_analyst/e2e/coach-150q.spec.ts` + helpers. Zero
production code.

(a) **Locator precision for richer answers** — `.matrix-card` /
    `.drills-list` assertions must tolerate ≥1 element (match `.first()` or
    scope to the answer's primary block, never strict-mode on
    multi-element). Covers PR-04 (2 matrices: Handspring Progress Matrix +
    Session comparison) and TP-02 (3 drill groups).

(b) **Fix the `.auth/state.json` mid-run wipe race** — isolate per-run auth
    path or prevent cross-run unlink. Diagnose root cause first (who unlinks
    / rewrites the file mid-run), then fix.

(c) **GATE tally must read the SAME transcript the per-test runs write** —
    fix the isolation/emptying (per-test transcript isolation empties the
    tally source, so GATE tallied `video_analysis 0/5` despite 5/5 passing).
    Diagnose first (which isolation step empties/moves the source), then fix
    so the tally source and the per-test writer agree.

Out of scope: any production code (analyst graph, shaping, routing,
retrieval); tier-marker emission (144 owns that); blank-retry semantics
(142 owns those).

## Validation Plan

1. PR-04/TP-02 specs pass against richer answers (2 matrices / 3 drill
   groups) across repeated runs — no strict-mode violations.
2. RE-05 runs without `Error reading storage state` across repeated runs
   (race gone, root cause documented).
3. GATE tally equals per-flow counts on a green run (e.g. video_analysis
   tally 5/5 when all 5 VA pass) — isolation/emptying fixed and documented.
4. Full spec file still green (no regressions in VA/PR/TP/IN/RE asserts).

## Acceptance Criteria

- [ ] PR-04/TP-02 tolerate 2 matrices / 3 drill groups (no strict-mode
      failure; assertion scoped to `.first()` or primary block).
- [ ] RE-05 no storage-state race (root cause diagnosed + documented, fix
      verified over repeated runs).
- [ ] GATE tally matches per-flow counts (tally reads the same transcript
      the per-test runs write; root cause diagnosed + documented).
- [ ] Zero production code changed.

## Dependencies

- **Blocked By**: — (implement sequentially with 144 only to avoid
  shared-file conflicts, not a ticket dependency).
- **Blocks**: —.

## Estimated Effort

- [S] (spec/helpers hardening + root-cause notes, no production code)
