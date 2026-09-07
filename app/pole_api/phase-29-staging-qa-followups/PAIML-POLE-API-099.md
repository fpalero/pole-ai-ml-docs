# Ticket: PAIML-POLE-API-099

## Title
[Chatbot] Fix `OpenRouterLLM` test double: set `llm._timeout = 120.0` in `test_openrouter_chat_sends_max_tokens`

## Description
Phase 29 — see [PLAN_PHASE_29](../plan/PLAN_PHASE_29.md). QA follow-up family
(bundle 1 / 093 test file). Test-only fix, zero prod risk.

Root cause: the adopted deadline ticket `PAIML-POLE-API-095` (pole-ai-ml#250,
`phase-30-chatbot-turn-budget/`) made `OpenRouterLLM.chat()`
(`packages/chatbot/src/pole_chatbot/llm.py:352`) read `self._timeout`
(lines 390/392; default `120.0` set in `__init__`, line 311). The pre-existing
test `test_openrouter_chat_sends_max_tokens` in
`app/pole_api/tests/test_analyst_chatbot_093_followups.py` (~line 449–472)
builds its double via `OpenRouterLLM.__new__(OpenRouterLLM)` — bypassing
`__init__` — and sets `llm.model` / `llm._metrics` / `llm._http` but never
`llm._timeout`, so `chat()` raises `AttributeError` on clean develop.
Prescribed as a separate tiny ticket by the local review of PRs #253/#254
(not part of either PR's scope).

## What to Do (Implementation Steps)
- [ ] In `test_openrouter_chat_sends_max_tokens`
  (`app/pole_api/tests/test_analyst_chatbot_093_followups.py`, ~line 472,
  alongside the existing `llm.model` / `llm._metrics` / `llm._http`
  assignments), add one line: `llm._timeout = 120.0` (mirrors the
  `OpenRouterLLM.__init__` default for `timeout=None`/non-positive).
- [ ] No prod-code change. No other test file touched.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `test_openrouter_chat_sends_max_tokens` passes on clean develop.
- [ ] No production code modified (test-only diff, single line).
- [ ] No coverage gate beyond the single test passing.

## Integration Tests to Run (Local Verification)
- [ ] `pytest app/pole_api/tests/test_analyst_chatbot_093_followups.py::test_openrouter_chat_sends_max_tokens`

## Dependencies
- **Blocks**: None (test-only; unblocks green develop for #253/#254 follow-ups).
- **Blocked By**: `PAIML-POLE-API-095` (the `self._timeout` read it adapts to;
  already merged).

## Estimated Effort
- [XS]
