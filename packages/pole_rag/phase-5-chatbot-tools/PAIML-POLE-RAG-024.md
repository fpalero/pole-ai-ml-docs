# Ticket: PAIML-POLE-RAG-024

## Title
[Application] Register 4 sync query tools in chatbot ToolRegistry

## Description
Phase 5: register `query_pole`, `query_calisthenics`, `query_psicology`,
`query_biomechanics` as sync `ToolSpec`s in the chatbot (`register_default_tools` or a
`rag_tools.py` slice). Each queries its Chroma DB via `pole_rag` with default k=3.
Tools are internal — not exposed as public HTTP endpoints.

## What to Do (Implementation Steps)
- [ ] Step 1: Add a `rag_tools.py` (or extend `tools.py`) in
      `packages/chatbot/src/pole_chatbot/` with 4 `ToolSpec`s:
      `query_pole`→`pole`, `query_calisthenics`→`calisthenics`,
      `query_psicology`→`psicology`, `query_biomechanics`→`biomechanics`.
- [ ] Step 2: Each spec: parameters `{query: string (required), k: integer (default 3),
      data_dir: string (optional default `config.default_data_dir()`)}`, mode `sync`.
- [ ] Step 3: Handlers call `pole_rag.query(db_name, query, k=k, data_dir=data_dir)` and
      serialize top-k (text/caption + `source_document` + `image_path`).
- [ ] Step 4: Unknown/empty DB → `ToolError` with actionable message.
- [ ] Step 5: Wire the 4 specs into `register_default_tools` (or a new registration
      entry point used by the app wiring).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] The code compiles/lints without errors.
- [ ] All 4 tools appear in the registry with correct names/params/mode.
- [ ] Each handler returns k=3 results with metadata (UC-07).
- [ ] Unit tests are written and passing for this specific component (temp Chroma).
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-07: each tool returns top-k with `source_document`.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-025, PAIML-POLE-RAG-026
- **Blocked By**: PAIML-POLE-RAG-019, PAIML-POLE-RAG-023

## Estimated Effort
- [M]