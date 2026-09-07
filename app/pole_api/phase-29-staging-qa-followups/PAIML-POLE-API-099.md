# Ticket: PAIML-POLE-API-099

## Title
[Chatbot] Reviewer-noted leftovers from #253/#254: test-double timeout, fallback type hint, None-safe blank check, ENV_VARS rows (no behavior change)

## Description
Phase 29 — see [PLAN_PHASE_29](../plan/PLAN_PHASE_29.md). Micro-bundle of
reviewer-noted leftovers from `pole-ai-ml` PRs #253/#254 (all verified, none
blocking). Explicitly tiny scope (4 items, est. <1h). No behavior change —
test-only fix, type-hint widening, None-safe guard with identical semantics on
valid inputs, and two missing `ENV_VARS.md` rows for vars introduced by
`PAIML-POLE-API-097`.

Items:

1. **`test_openrouter_chat_sends_max_tokens` test-double fix.** `OpenRouterLLM`
   instances built via `__new__` lack `_timeout` (added by 095 per-call
   budget) → one-line fix setting `llm._timeout = 120.0` in
   `app/pole_api/tests/test_analyst_chatbot_093_followups.py:448-476`.
   Test-only change; currently the single red test in 096's suites (proven
   pre-existing on clean develop).
2. **Type-hint nit:** `packages/chatbot/src/pole_chatbot/agent_langgraph.py:289`
   — `fallback_llm: OllamaLLM | None` but `main.py` passes `OpenRouterLLM`;
   widen to union or Protocol.
3. **Robustness nit:** `agent_langgraph.py:1108` log-only
   `if not reply.strip()` → None-safe (`is_blank_completion(...)` or
   `(reply or "").strip()`).
4. **`ENV_VARS.md` rows** for the two 097 vars (`CHATBOT_BLANK_MAX_RETRIES`
   default 2, `OPENROUTER_FALLBACK_MODEL` default unset/disabled).

## What to Do (Implementation Steps)
- [ ] (1) In `test_analyst_chatbot_093_followups.py:448-476`, set
  `llm._timeout = 120.0` on the `__new__`-built `OpenRouterLLM` double so the
  095 per-call budget path has the attribute it reads. Assert the named test
  goes green; assert no production-code change in the diff.
- [ ] (2) Widen the `fallback_llm` annotation at `agent_langgraph.py:289` to
  accept `OpenRouterLLM` (union or Protocol). No runtime change — annotation
  only; assert `main.py` type-checks against it.
- [ ] (3) Make the log-only blank check at `agent_langgraph.py:1108`
  None-safe — reuse `is_blank_completion(...)` where it matches 097 semantics,
  else `(reply or "").strip()`. Assert identical behavior on str inputs (no
  behavior change; regression test with `None` reply completes without
  `AttributeError`).
- [ ] (4) Add the two missing `ENV_VARS.md` rows: `CHATBOT_BLANK_MAX_RETRIES`
  (default 2) and `OPENROUTER_FALLBACK_MODEL` (default unset/disabled),
  matching the 097 implementation defaults.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `test_openrouter_chat_sends_max_tokens` green.
- [ ] Full affected suites green (`pixi run test-api` + `pixi run test-chatbot`),
  coverage ≥ 80%.
- [ ] No behavior change: diff is test-only (1), annotation-only (2),
  semantics-preserving guard (3, asserted by tests where feasible), docs-only
  (4).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs) — named test green, suite green.
- [ ] `pixi run test-chatbot` (guarded `_testing` DBs) — suite green.

## Dependencies
- **Blocks**: None (polish bundle; backend-only, no contract change).
- **Blocked By**: None. Related: `PAIML-POLE-API-095` (per-call `_timeout`
  budget, item 1), `PAIML-POLE-API-097` (blank hardening + the two env vars,
  items 3–4), `PAIML-POLE-API-096` (whose suites surface the single red test,
  item 1). Reviewer notes from `pole-ai-ml` PRs #253/#254.

## Estimated Effort
- [XS] (<1h)
