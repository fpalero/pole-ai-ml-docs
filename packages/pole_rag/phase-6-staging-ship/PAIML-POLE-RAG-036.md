# Ticket: PAIML-POLE-RAG-036

## Title
[Fix] psychology DB-name mapping (query_psicology -> psychology)

## Description
Phase 6 staging-ship follow-up (blocker B). The uploaded DB dir is
`/data/rag/psychology` (correct spelling, user decision option b) but
`packages/chatbot/src/pole_chatbot/rag_tools.py` line 27 maps
`"query_psicology": "psicology"`, so the `query_psicology` tool resolves to a
nonexistent dir while `/data/rag/psychology` (4365 text + 1633 images,
verified on-pod) sits unused. One-line mapping fix; tool name stays.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Step 1 [pole-ai-ml]: Change `RAG_DB_BY_TOOL["query_psicology"]` from
      `"psicology"` to `"psychology"` in
      `packages/chatbot/src/pole_chatbot/rag_tools.py` (line 27).
- [ ] Step 2 [pole-ai-ml]: Keep the tool NAME `query_psicology` unchanged
      everywhere (tool registry, prompts, callers) — only the mapping value
      changes.
- [ ] Step 3 [pole-ai-ml]: Add/adjust a mapping assertion test
      (`RAG_DB_BY_TOOL["query_psicology"] == "psychology"`).
- [ ] Step 4 [pole-ai-ml]: Fix any `psicology` DB-path references in
      docstrings/comments touched by the change (no drive-by renames outside
      the touched lines).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Chatbot + rag unit tests green (including the new mapping assertion).
- [ ] `query_psicology` tool resolves to `/data/rag/psychology` on staging
      (full end-to-end proof is ticket 030).

## Integration Tests to Run (Local Verification)
- [ ] Mapping unit test: `RAG_DB_BY_TOOL["query_psicology"] == "psychology"`.
- [ ] `pixi run test-chatbot` + `pixi run test-rag` green before ship.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-030
- **Blocked By**: —
  (independent, parallel with PAIML-POLE-RAG-035 — no ordering constraint)

## Estimated Effort
- [S]
