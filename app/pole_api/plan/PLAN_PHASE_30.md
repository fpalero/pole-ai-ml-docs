# Fase 30 — Chatbot resilience: empty-reply recovery + RAG picture blocks — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Origen: staging evidence — picture/anatomy turns return
> blank `content` + no `tool_calls` from llama-3.3-70b (OpenRouter); `agent.run()` converts the
> blank to `FALLBACK_MESSAGE` (`status=ACTIVE iteration=0`), and no retry ever fires.

## Contexto

Staged failures on `kubectl logs -n pole-ai deploy/pole-ai-pole-api` showed:

```text
WARNING agent: empty reply with no tool calls -> FALLBACK_MESSAGE;
  final_state status=ACTIVE iteration=0 pending=[]
```

at 10:36:27 / 10:37:22 / 10:38:06 (matching the failing picture questions). Zero
malformed-JSON / unknown-tool warnings — the rephrase budget is NOT the cause.

Two compounding defects:

1. **`app/pole_api/src/analyst_chatbot/services.py`** — the degenerate-retry check
   `is_degenerate_reply(FALLBACK_MESSAGE)` is `False` (non-empty string), so the blank-originated
   fallback never triggers a retry.
2. **`packages/chatbot/src/pole_chatbot/agent_langgraph.py`** — `_call_model_node` reads
   `content or ""` + `tool_calls or []`; `_route_after_model` finalizes immediately when
   `pending=[]`, so a blank reply ends the loop at `iteration=0`, bypassing `max_iterations`.

Additionally the prompt never forbids empty replies, and RAG image hits (`image_path` in Chroma
metadata) have no display path: no `image` block type, no serving endpoint, no FE rendering.

## Tickets

| Ticket | Scope | Estado |
| :--- | :--- | :--- |
| `PAIML-POLE-API-090` | Empty-reply retry (services) + graph-level loop guard (shared core) + prompt hardening + RAG picture `image` blocks (block type, serving endpoint, FE rendering) + offline-embedding guarantee | 📋 PLANNED |

## Tasks

- **Fix 1 — empty-reply retry** (`analyst_chatbot/services.py`): after `run()`, if
  `reply == FALLBACK_MESSAGE` and `session_status != ABANDONED`, do ONE fresh re-run with a
  recovery nudge appended to the assistant messages — capped to one retry.
- **Fix 2 — graph-level loop guard** (`pole_chatbot/agent_langgraph.py`): when `reply == ""`
  and `pending == []` and `iteration < max_iterations`, route back to `call_model` with a
  recovery nudge instead of finalize. Keep `max_iterations` authoritative (no infinite loops).
  Shared core — benefits the training chatbot too.
- **Fix 3 — prompt hardening** (`analyst_chatbot/prompts.py` `ANALYST_SYSTEM_PROMPT`):
  (a) NEVER return an empty response; (b) picture asks must answer with an `image` block or a
  tool call, never blank.
- **Fix 4 — RAG picture display (new)**: `image` block type in `blocks.py` (+ prompt
  vocabulary); path-traversal-guarded serving endpoint for `POLE_RAG_DATA_DIR` images
  (per-image relative `image_path` from Chroma metadata); prompt rule to emit `image` blocks
  from RAG hits; FE `@case ('image')` rendering in `chat-pane.component.ts` + block model
  update in `chat-message.ts`.
- **Fix 5 — offline embedding guarantee (codify)**: `embeddings.py` never downloads (raises
  naming the model if missing); acceptance = zero HF-hub traffic at runtime in staging + local
  dev (`HF_HUB_OFFLINE=1`-equivalent harness).

## Acceptance

- Blank first-call replies are retried once (services) / looped with a nudge (graph) instead
  of finalizing at `iteration=0`; `max_iterations` still caps the loop.
- Picture questions always produce an `image` block or a tool call, never blank.
- RAG `image_path` hits render as served images with caption + source in the FE.
- No HuggingFace hub network calls at runtime in either env.
- `pixi run test-api` green, coverage ≥ 80%.

## Dependencies

- **Blocks:** None (single ticket; independent of phase-29 088/089).
- **Blocked By:** None.
