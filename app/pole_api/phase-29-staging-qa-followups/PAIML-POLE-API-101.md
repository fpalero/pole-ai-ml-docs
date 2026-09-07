# Ticket: PAIML-POLE-API-101

## Title
[Chatbot] Salvage of closed docs PR #29 live items: `fallback_llm` type hint, None-safe blank check, `ENV_VARS.md` rows (no behavior change)

## Description
Phase 29 — see [PLAN_PHASE_29](../plan/PLAN_PHASE_29.md). Salvage of the
unmerged docs PR `pole-ai-ml-docs#29` (CLOSED, unmerged — 4-item polish bundle
from the local review of `pole-ai-ml#253`/`#254`, all verified, none blocking).

- **Item 1 of #29 is DONE elsewhere — pointer only, not re-documented here:**
  the `test_openrouter_chat_sends_max_tokens` test-double fix
  (`llm._timeout = 120.0`) shipped via code `pole-ai-ml#259` (merged) +
  docs `pole-ai-ml-docs#30` (merged, canonical ticket
  `phase-29-staging-qa-followups/PAIML-POLE-API-099.md`).
- **This ticket carries the 3 remaining live items** (zero behavior change —
  annotation-only, semantics-preserving guard, docs-only):

1. **Widen `fallback_llm` type hint / annotation**
   (`packages/chatbot/src/pole_chatbot/agent_langgraph.py:289`,
   `fallback_llm: OllamaLLM | None`) — `app/pole_api/main.py` passes an
   `OpenRouterLLM` (built at `main.py:587`, wired at `main.py:601`); widen the
   hint to union/Protocol. No runtime change.
2. **None-safe log-only blank check** (`agent_langgraph.py:1108`,
   `if not reply.strip()` → reuse `is_blank_completion(...)` from
   `blank_policy.py` (097 semantics) or `(reply or "").strip()`; identical
   behavior on str inputs).
3. **`ENV_VARS.md` rows for the two 097 vars** (`CHATBOT_BLANK_MAX_RETRIES`
   default 2, `OPENROUTER_FALLBACK_MODEL` default unset/disabled), matching
   the 097 implementation defaults (`app/pole_api/src/core/config.py`:
   `chatbot_blank_max_retries` defaults to 2,
   `openrouter_fallback_model` defaults to `None`).

## Numbering
- Uses **101** for this ticket; never touches `098`/`100`.
- `100` = `phase-32-english-only/PAIML-POLE-API-100.md` (parallel session
  `pole-ai-ml#257` code + `pole-ai-ml-docs#31` docs, both merged).

## What to Do (Implementation Steps)
- [ ] (1) Widen the `fallback_llm` type hint (annotation) at `agent_langgraph.py:289` to
  accept `OpenRouterLLM` (union or Protocol). No runtime change — hint
  only; assert `main.py` type-checks against it.
- [ ] (2) Make the log-only blank check at `agent_langgraph.py:1108`
  None-safe — reuse `is_blank_completion(...)` where it matches 097 semantics,
  else `(reply or "").strip()`. Assert identical behavior on str inputs (no
  behavior change; regression test with `None` reply completes without
  `AttributeError`).
- [ ] (3) Add the two missing `ENV_VARS.md` rows: `CHATBOT_BLANK_MAX_RETRIES`
  (default 2) and `OPENROUTER_FALLBACK_MODEL` (default unset/disabled),
  matching the 097 implementation defaults.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] (1) Annotation type-checks: `main.py` (`OpenRouterLLM` fallback) passes
  against the widened hint.
- [ ] (2) None-regression test: `None` reply completes without
  `AttributeError`; identical behavior on str inputs.
- [ ] (3) ENV rows present in `ENV_VARS.md` with the 097 defaults.
- [ ] No behavior change: diff is annotation-only (1),
  semantics-preserving guard (2, asserted by tests where feasible), docs-only
  (3).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs) — suite green.
- [ ] `pixi run test-chatbot` (guarded `_testing` DBs) — suite green.

## Dependencies
- **Blocks**: None (polish bundle; backend-only, no contract change).
- **Blocked By**: None. Related: `PAIML-POLE-API-095` (turn budget, fallback
  wiring context), `PAIML-POLE-API-097` (blank hardening + the two env vars,
  items 2–3), `PAIML-POLE-API-099` (sibling #29 item 1, done via
  `pole-ai-ml#259` + `pole-ai-ml-docs#30`). Reviewer notes from `pole-ai-ml`
  PRs #253/#254; salvage of closed `pole-ai-ml-docs#29` items 2–4.

## Estimated Effort
- [XS] (<1h)
