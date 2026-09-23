# Ticket: PAIML-POLE-API-142

## Title
RE-05 blank death with no retry trace — forensics first (135 retry fired-but-unlogged vs ReAct-path coverage gap)

- **Status**: 📋 PLANNED
- **Project**: pole_api (analyst graph / ReAct turn path)
- **Phase**: 42 coach-gate-25
- **Blocks**: —
- **Blocked By**: — independent of 143 (implement sequentially only to avoid shared-file conflicts, not a ticket dependency).

## Context

Local SAMPLE-5 21/25 (run `20260923-205700` + targeted rerun; report
`docs/app/pole_api/phase-42-coach-gate-25/LOCAL_GATE_20260923_2125.md` — binding
evidence). Images from develop `66a9d83` (124–141 all live, verified in-pod).
All real data, no mocks.

Prior tickets cover: 134 tiers, 135 blank-retry (2 shared retries,
graph-finalize + VA nodes), 136 determinism, 140 md-first, 141 tier asserts.

Forensics evidence (binding, proven): turn `ws=c88b0615-...` (2026-09-23 20:14
UTC) ran 42s, all OpenRouter calls HTTP 200, finalized ABANDONED with empty
reply/blocks/tools; **zero** blank/repair/retry/exhaust log lines in 90 min of
pod logs.

Two hypotheses (determine first, then fix):
- (a) 135's retry fired but logs at DEBUG (logging gap — raise to INFO).
- (b) This ReAct-level blank path bypasses both graph-finalize and VA-node
  retries (coverage gap).

## Scope

1. **Forensics first:** reproduce/determine via pod logs + hermetic replay
   which hypothesis holds — (a) retry fired but unlogged, or (b) ReAct-level
   blank path bypasses 135's graph-finalize + VA-node retries.
2. **Minimal fix after determination:** log-level raise (DEBUG → INFO) and/or
   extend retry coverage to the ReAct blank path. No budget/ladder changes;
   no tier-semantics changes (134 owns those); no md-first changes (140 owns
   those).

Out of scope: production behavior beyond the blank-path retry/logging fix;
touching 134/140/141 semantics.

## Validation Plan

1. Hermetic replay of a forced-blank ReAct turn: blank triggers visible retry
   evidence (INFO-level blank/repair/retry log lines).
2. ABANDONED-after-budget preserved: turn terminates bounded when all retries
   return blank (genuine failure), never on first blank.
3. Log grep over the turn window shows retry lines (no more zero-trace deaths).

## Acceptance Criteria

- [ ] A forced-blank ReAct turn shows retry log lines (hypothesis resolved and
      documented: (a) logging gap and/or (b) coverage gap fixed).
- [ ] Turn terminates bounded; no infinite loops.
- [ ] ABANDONED appears only after retry budget exhaustion (genuine failure).
- [ ] No budget/ladder changes; no tier-semantics changes.

## Dependencies

- **Blocked By**: — (implement sequentially with 143 only to avoid
  shared-file conflicts, not a ticket dependency).
- **Blocks**: —.

## Estimated Effort

- [S] (forensics via logs + hermetic replay, then minimal log/coverage fix)
