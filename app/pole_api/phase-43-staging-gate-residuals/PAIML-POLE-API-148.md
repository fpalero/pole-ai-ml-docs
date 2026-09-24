# Ticket: PAIML-POLE-API-148

## Title
VA tail-latency flake: gate-side per-turn retry for timeout turns + server progress-frames record (OpenRouter deepseek-v4-flash)

- **Status**: 🟢 IN REVIEW (code PR open; staging gate re-run pending)
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

## Investigation: OpenRouter tail (findings, 2026-09-24)

Read — not invented (all paths below verified on `develop`):

- **Model pin.** Staging serves `deepseek/deepseek-v4-flash`
  (`infrastracture/helm/pole-ai/values.yaml:132`,
  `values-dev.yaml:78`); the code default is
  `meta-llama/llama-3.3-70b-instruct`
  (`app/pole_api/src/core/config.py:78`). The gate comment in
  `coach-150q.spec.ts` records live-turn shape: ~115s+ typical with
  OpenRouter tail calls of 25–52s × ~5 per turn.
- **Timeout stack (all budgets intact, none raised here).** Per-call HTTP
  timeout defaults to 120s (`OpenRouterLLM._timeout`,
  `packages/chatbot/src/pole_chatbot/llm.py`), tightened per call to the
  turn's remaining budget (095). The composed turn is bounded by
  `SUPERGRAPH_TURN_BUDGET_S = 30.0`
  (`analyst_chatbot/coach_providers.py:95`), the 129 ReAct sub-budget
  (`CHATBOT_TURN_TIMEOUT`, 240s default), and the 126 WS wall-clock guard
  (`analyst_ws_turn_budget_s`, 300s default, `router.py`) which emits the
  terminal `agent_reply` frame `status: "error"` +
  `error_code: "turn_timeout"`. Arithmetic of the flake: every turn blows
  the 30s brain budget (staging logs confirm `delegating` every turn), so
  all reasoning rides the ReAct chain; on a tail turn 5 × ~50s calls ≈
  250s+ ReAct time, past the 300s WS guard or the 360s FE wait → the
  observed VA-05 signature (no `md` + `analysis_link` inside the budget).
- **No in-request failover.** The OpenRouter payload is
  `model/messages/temperature/tools` only (`llm.py: chat()`) — no
  `provider: { order, allow_fallbacks }` routing, no `models` fallback
  array, no `max_price` cap. A slow provider stays slow for the whole turn.
- **097 fallback exists but is inert on staging.** `main.py` wires
  `OPENROUTER_FALLBACK_MODEL` as a single fallback attempt for
  blank-exhausted turns — but staging helm sets
  `openrouterFallbackModel: ""` (`values.yaml:133`), so the path is
  disabled where the flake bites (dev pins
  `qwen/qwen-2.5-coder-32b-instruct`, `values-dev.yaml:79`).
- **Tail-latency signature (not a regression).** Same timeout signature on
  different turns across runs (VA-04 → VA-05): per-turn latency draw from
  the shared `deepseek-v4-flash` provider, uncorrelated with question
  content or the 146/147 shaping work. No product code changed between the
  runs that would explain a turn migration.

Model/timeout options considered and DEFERRED (out of scope — no
production code in this ticket; candidates for a follow-up ticket):

1. Set `openrouterFallbackModel` in staging helm (enables the existing
   097 path; one-line values change, needs its own ticket + gate run).
2. OpenRouter `provider` routing / `models` array for automatic
   in-request failover on timeout (payload change in `llm.py`).
3. Tighter per-call timeout for the VA-heavy supergraph path so the tail
   degrades to ReAct sooner instead of burning the whole turn budget.

## Implementation (code PR, test-only)

- NEW `app/pole_analyst/e2e/turn-retry.ts` — pure policy (zero
  Playwright imports): `TAIL_RETRY_MAX_ATTEMPTS = 1`,
  `isTurnWaitTimeout` (Playwright `Timeout <n>ms exceeded`, mirroring the
  132 `isWaitForUrlTimeout` precedent), `isTimeoutFrame` (126
  `turn_timeout` terminal frame only), `shouldRetryTimeoutTurn`
  (timeout-only AND attempts remain), and `sendWithTailRetry` (the wiring
  the gate uses: wait-timeout → resend once; `turn_timeout` frame →
  resend once; anything else propagates/returns untouched; never chained).
- `coach-150q.spec.ts` — per-question turn goes through
  `sendWithTailRetry`; retry recorded per turn as
  `timeout_retry: 'none' | 'retried-once'` in the transcript row
  (additive — GATE tally reads `id`/`flow`/`verdict` only). Shared path
  (flow-agnostic) but timeout-only, so VA-05 is covered without
  flow-specific branching; budgets untouched.
- `helpers.ts` — re-exports the policy (single import point for specs).
- NEW `turn-retry.spec.ts` — 9-case harness self-test through the REAL
  wiring with stubbed senders: flaky-once succeeds after one resend,
  persistent tail propagates after exactly 2 sends, non-timeout failure
  sends once, `turn_timeout` frame resends / ok + non-timeout error
  frames never resend. Server-free (pure, no fixtures).
- Evidence (code branch): 9/9 self-test green; `tsc` parity with
  `develop` (24 pre-existing node-types noise lines both sides, zero new);
  eslint clean on new files (3 `Array<T>` errors in the gate spec are
  pre-existing on `develop`); gate `--list` FULL 153 / SAMPLE-5 28 tests
  intact. Full 25-turn staging re-run (validation item 1) is phase-end QA
  on the staging stack, not pre-PR.

## FUTURE: server-side progress-frames (recorded, not built)

Follow-up design for the dead-turn problem (FE 360s budget sees no
liveness during a long ReAct chain): the WS handler emits lightweight
`agent_progress` frames (turn id + elapsed + completed tool-call count,
no LLM prose) at a fixed cadence while `run_turn` is in flight; the FE
`processing` pill resets its liveness timer on each frame instead of the
single 360s wall clock. Acceptance sketch: re-run VA-05 against a tail
stack — the turn shows continuous progress frames and either completes
with `md` + `analysis_link` or terminates with the existing
`turn_timeout` frame; zero turns end with zero frames of any kind inside
360s. No production code in this ticket.
