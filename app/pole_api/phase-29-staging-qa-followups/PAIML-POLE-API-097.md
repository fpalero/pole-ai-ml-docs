# Ticket: PAIML-POLE-API-097

## Title
[Chatbot] Blank-completion hardening: blank-detection + retry budget + model fallback (no ~152s hangs)

## Description
Phase 29 — see [PLAN_PHASE_29](../plan/PLAN_PHASE_29.md). Fourth bundle from the
staging QA gate-2 rerun (tester evidence, local, not committed):
`/tmp/opencode/staging-gate2/` (`summary.json`, `RAG-*.json`).

Root cause established by the rerun (backend completion handling):

- (F4) **Empty LLM completions hang the turn ~152s, then ABANDONED.** The
  RAG-class questions `RAG-06` (152559ms), `RAG-07` (152561ms), `RAG-09`
  (152565ms), `RAG-10` (152569ms), `RAG-12` (152570ms), `RAG-13` (152569ms),
  `RAG-14` (152567ms) each hang for ~152s and end on the error chip with the
  generic `analysis_failed` reply (`summary.json`: `"chip": "Error"`,
  `"renderedBlocks": ["md"]` with `md: 0` cards, empty `replyHead`). Per the
  gate brief these are blank completions from the provider: the turn waits out
  timeouts instead of detecting the blank, retrying within a budget, or falling
  back to another model — so a trivially recoverable provider hiccup becomes a
  ~152s user-visible hang ending ABANDONED.

## What to Do (Implementation Steps)
- [ ] (F4) Add blank-completion detection on every LLM response in the chatbot
  turn path (`packages/chatbot/`, agent + LLM adapters): treat empty/whitespace-only
  content with no tool calls as a blank (not an answer, not a turn end).
- [ ] Add a bounded retry budget for blanks (small N, documented; each retry
  counts against the turn's wall-clock budget from `PAIML-POLE-API-095`, never
  extends it).
- [ ] Add model fallback: when the retry budget for blanks is exhausted (or the
  provider blank-rate trips a threshold), re-issue the call on the fallback
  model instead of hanging to ABANDONED. Document the fallback order and keep
  the staging model pin (`OPENROUTER_MODEL=deepseek/deepseek-v4-flash`, recorded
  in `PAIML-POLE-API-095`) as the primary.
- [ ] Surface a still-failing turn through the normal failed-turn signal
  (`PAIML-POLE-API-093(d)` error status) — never a silent hang, never a generic
  `analysis_failed` prose-only dead end without the machine-readable status.
- [ ] Add/update tests (`packages/chatbot/tests/`,
  `app/pole_api/tests/test_analyst_chatbot*.py`): blank completion → retry →
  fallback → graceful error; RAG-06-class questions complete or fail fast
  (assert turn duration far below the ~152s hang).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] (F4) RAG-06/07/09/10/12/13/14-class questions no longer hang ~152s on
  blank completions: blanks are detected, retried within budget, then model
  fallback — the turn answers or fails fast with the 093(d) error signal.
- [ ] Retry/fallback never exceed the `PAIML-POLE-API-095` turn wall-clock
  budget (coordinate acceptance with 095: deadlines change hang behavior —
  a deadline-expired turn answers gracefully ACTIVE per 095; a blank-exhausted
  turn surfaces the 093(d) error status; the two paths must not mask each other).
- [ ] `pixi run test-api` + `pixi run test-chatbot` green, coverage ≥ 80%.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-chatbot` and `pixi run test-api` (guarded `_testing` DBs)
- [ ] Staging rerun of the RAG battery (`RAG-01..20`): no ~152s hangs; blank
  provider responses recover via retry/fallback or fail fast with error status.

## Dependencies
- **Blocks**: None (backend-only; FE already renders the 093(d) error state via
  `PAIML-POLE-ANALYST-073`).
- **Blocked By**: None. Evidence paths above are local tester artifacts.
  Related: `PAIML-POLE-API-095` (turn deadlines bound the retry budget —
  coordinate acceptance so deadline-expiry and blank-exhaustion stay
  distinguishable).

## Estimated Effort
- [M]
