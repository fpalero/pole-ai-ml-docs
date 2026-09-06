# Ticket: PAIML-POLE-API-090

## Title
[Chatbot] Empty-reply recovery + RAG picture blocks (offline embeddings)

## Description
Phase 30. Staging evidence (`kubectl logs -n pole-ai deploy/pole-ai-pole-api`):

```text
WARNING agent: empty reply with no tool calls -> FALLBACK_MESSAGE;
  final_state status=ACTIVE iteration=0 pending=[]
```

at 10:36:27 / 10:37:22 / 10:38:06 — matching the failing picture questions. Zero
malformed-JSON / unknown-tool warnings, so the rephrase budget is NOT the cause.

Root cause is a staged empty-reply failure: the LLM (llama-3.3-70b via OpenRouter) returns
blank `content` + no `tool_calls` on the FIRST call of picture/anatomy turns; `agent.run()`
converts the blank to `FALLBACK_MESSAGE` with `status=ACTIVE iteration=0`. The current
degenerate-retry check `is_degenerate_reply(FALLBACK_MESSAGE)` is `False` (non-empty string),
so no retry ever fires. At the graph level, `_call_model_node` reads `content or ""` +
`tool_calls or []` and `_route_after_model` finalizes immediately when `pending=[]` — the
blank reply ends the loop at `iteration=0`, bypassing `max_iterations`.

This ticket fixes recovery at both levels, hardens the prompt against empty replies, adds a
first-class RAG picture display path (`image` blocks served from `POLE_RAG_DATA_DIR`), and
codifies the offline-embedding guarantee.

## What to Do (Implementation Steps)
- [ ] **Fix 1 — empty-reply retry** (`app/pole_api/src/analyst_chatbot/services.py`): after `run()`, if result `reply == FALLBACK_MESSAGE` and `session_status != ABANDONED`, do ONE fresh re-run with a recovery nudge (e.g. append a short "The previous answer was empty; respond normally" instruction to the assistant messages) — capped to one retry.
- [ ] **Fix 2 — graph-level loop guard** (`packages/chatbot/src/pole_chatbot/agent_langgraph.py`): in `_route_after_model` / `_finalize_node`, when `reply == ""` and `pending == []` and `iteration < max_iterations`, route back to `call_model` with a recovery nudge (e.g. an injected system/assistant message "Provide a substantive answer; do not return empty.") instead of finalize. Shared core — benefits the training chatbot too. Keep `max_iterations` cap authoritative (no infinite loops).
- [ ] **Fix 3 — prompt hardening** (`app/pole_api/src/analyst_chatbot/prompts.py` `ANALYST_SYSTEM_PROMPT`): add explicit rules — (a) NEVER return an empty response; if you cannot satisfy the request, say so in a normal `md` block; (b) for picture/visual asks, prefer emitting an `image` block from a RAG hit's `image_path` when available, else use `extract_frames` / `frame_pose` tool outputs — an `image` block or a tool call is the ONLY acceptable answer to a picture question, never blank.
- [ ] **Fix 4 — RAG picture display (new)**:
  - [ ] New block type `image`: `{type: "image", src: str, caption?: str, source_document?: str}` in `app/pole_api/src/analyst_chatbot/blocks.py` — add to `VALID_TYPES`, parse/serialize, and the prompt's block vocabulary. Mirrors the FE's existing `<img [src]="block.thumbnail_url">` rendering pattern.
  - [ ] RAG image serving: a path-traversal-guarded endpoint in `app/pole_api` that serves image files from `POLE_RAG_DATA_DIR` (staging = `/data/rag`, local dev = `packages/pole_rag/data`) using per-image relative paths stored in Chroma metadata (`image_path`). e.g. `GET /api/rag-images/{db}/...` where `db` resolves to a known DB directory and the remaining path is validated against the resolved directory (reject `..`, symlink escapes, absolute paths). Reference: `packages/pole_rag/src/pole_rag/seeder.py` (metadata `image_path`, `image_title`, `type:"image"`), `packages/chatbot/src/pole_chatbot/rag_tools.py` `_serialize_hit` (already returns `image_path`), `packages/pole_rag/src/pole_rag/query.py` (returns `metadata`).
  - [ ] Prompt rule: when a RAG hit includes `image_path` and the user asks about that trick/anatomy/position, emit an `image` block with `src` = served URL + caption (e.g. `image_title` / source_document).
  - [ ] FE rendering: `app/pole_analyst/src/app/features/chat/components/chat-pane/chat-pane.component.ts` new `@case ('image')` rendering `<img>` + caption + source link (follow the existing `@case ('video_segment')` thumbnail pattern); block model update in `app/pole_analyst/src/app/features/chat/models/chat-message.ts`.
- [ ] **Fix 5 — offline embedding guarantee (codify, mostly verified):** `packages/pole_rag/src/pole_rag/embeddings.py` is already designed to never download (raises naming the model if missing locally). Staging pod verified: `HF_HUB_OFFLINE=1`, model cached in-pod, `/data/rag` populated, zero hub traffic in logs. Local dev verified: model is in the local HF cache. Acceptance criterion: no HuggingFace hub network calls at runtime in either env; test/env harness sets `HF_HUB_OFFLINE=1`-equivalent (e.g. unit test asserts embedder loads from local cache without a hub hit, or a deployment check). No new download machinery.
- [ ] Add/update tests in `app/pole_api/tests/test_analyst_chatbot*.py` (empty-reply retry fires once; graph guard re-routes blank replies; `image` block parse/serialize; serving endpoint rejects traversal) and chatbot package tests (loop-guard).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Blank first-call replies trigger ONE services-level re-run (capped) and graph-level re-route to `call_model` with a recovery nudge instead of finalizing at `iteration=0`; `max_iterations` still caps the loop (no infinite loops).
- [ ] Picture/visual questions always produce an `image` block or a tool call, never a blank reply; prompt rules enforce non-empty responses.
- [ ] RAG `image_path` hits render as served images (`image` block with served-URL `src` + caption/source) in the FE chat pane; serving endpoint rejects `..`, symlink escapes, and absolute paths.
- [ ] No HuggingFace hub network calls at runtime in staging or local dev (`HF_HUB_OFFLINE=1`-equivalent harness green).
- [ ] Tests assert the retry, the loop guard, the `image` block round-trip, and the traversal guard.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: None
- **Blocked By**: None

## Estimated Effort
- [M]
