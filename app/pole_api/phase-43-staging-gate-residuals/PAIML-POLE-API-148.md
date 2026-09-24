# Ticket: PAIML-POLE-API-148

## Title
VA tail-latency flake: gate-side per-turn retry for timeout turns + server progress-frames record (OpenRouter deepseek-v4-flash)

- **Status**: 📋 PLANNED
- **Project**: pole_api (gate harness + analyst latency — test-only retry, server future)
- **Phase**: 43 staging-gate-residuals
- **Blocks**: —
- **Blocked By**: —

## Context

Staging SAMPLE-5 gate RUN_ID `20260924-163713` scored **22/25**: VA 4/5
(VA-05 timeout), RE 3/5 (RE-04 + RE-05). This ticket owns the VA-05 flake.

Binding evidence, written faithfully:

- Question: "Review my latest video: was my body angle consistent from
  ENTRANCE to EXIT?" expects `md` + `analysis_link`.
- Staging logs show `supergraph invoke exceeded 30.0s budget; delegating`
  every turn → ReAct chain → FE 360s budget overrun on the tail turn.
- Root suspect: OpenRouter `deepseek-v4-flash` tail latency — the flake
  migrated VA-04 → VA-05 across runs (same signature, different turn),
  i.e. a latency flake, not a product regression.
- Artifacts: `app/pole_analyst/test-results/coach-150q/20260924-163713/`.
- RAG ref: `pixi run docs-rag-read "coach-150q SAMPLE-5 25 questions gate" --k 5`.

Prior tickets cover: 126 WS per-turn wall-clock guard, 129 ReAct
sub-budget, 135 blank-retry on ABANDONED turns, 132 harness bootstrap
retry, 145 spec/harness hardening (test-only precedent).

## Scope

1. **Gate-side per-turn retry for timeout turns (harness, test-only)** —
   retry the timed-out VA turn once (timeout-only, no semantic retry),
   following the 132/145 test-only precedent. Assert the retry fires and
   the retried turn can reach `md` + `analysis_link`.
2. **Record server-side progress-frames as FUTURE** — document (no
   implementation) the server follow-up: streaming progress frames during
   long ReAct chains so the FE 360s budget sees liveness instead of a
   dead turn.

Constraints (hard-stops):

- Test-only for the retry (harness/spec files only — zero production code,
  mirroring 145).
- No budget inflation: do not raise the FE 360s or supergraph 30s budgets
  to "fix" the flake; retry is bounded (once, timeout-only).
- No mocks: real staging stack, real model path.
- 126/129/132/135/145 suites green.

Out of scope: any production-code latency fix (recorded as future only);
T2/T3 readiness shaping (146/147 own those); broadening retry to
non-timeout failures.

## Validation Plan

1. Re-run the VA-05 turn against a stack exhibiting the tail: without
   retry the turn times out; with retry the turn reaches `md` +
   `analysis_link`.
2. Negative: non-timeout failures do NOT retry (bounded, timeout-only).
3. Full gate-spec file still green (no regressions in VA/PR/TP/IN/RE asserts).
4. Server progress-frames design recorded as FUTURE with acceptance sketch.

## Acceptance Criteria

- [ ] Timeout turn retried once (harness, test-only) and reaches `md` +
      `analysis_link` when the tail clears.
- [ ] Retry is timeout-only and bounded (non-timeout failures never retry;
      budgets unchanged).
- [ ] Flake migration VA-04 → VA-05 documented as tail-latency signature
      (not a product regression).
- [ ] Server-side progress-frames recorded as FUTURE (no production code
      in this ticket).
- [ ] Zero production code changed.

## Dependencies

- **Blocked By**: — (independent of 146/147; harness-only so no
  shared-file conflict with shaping fixes).
- **Blocks**: —.

## Estimated Effort

- [S] (harness per-turn retry + root-cause note + future record, no production code)
