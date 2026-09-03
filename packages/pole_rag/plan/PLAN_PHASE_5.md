# PLAN PHASE 5 — Chatbot tool integration

> **Project:** `pole_rag` (cross-package: `chatbot`) · **State:** 📋 PLANNED ·
> **Back to:** [PLAN.md](../PLAN.md)

## Scope
Wire the 4 similarity tools into the chatbot ToolRegistry so the agent can query each
resource Chroma DB: `query_pole`, `query_calisthenics`, `query_psicology`,
`query_biomechanics` (sync, k=3 default). Tools are internal — not exposed as public
HTTP endpoints; the chatbot endpoint is already behind auth. Because `pole_rag` has **no pip
package**, the chatbot reaches `pole_rag` via workspace `PYTHONPATH` (not a dependency).

## Tasks
- [ ] Chatbot runtime includes `packages/pole_rag/src` on its `PYTHONPATH` (task env or
      launcher for `chatbot-api` / `test-chatbot` / `test-chatbot-live`); no
      `pole-rag` pip dependency added.
- [ ] `packages/chatbot/src/pole_chatbot/tools.py` (or a new `rag_tools.py` slice) —
      register 4 `ToolSpec`s:
      - `query_pole` → DB `pole`
      - `query_calisthenics` → DB `calisthenics`
      - `query_psicology` → DB `psicology`
      - `query_biomechanics` → DB `biomechanics`
      each with parameters `{query: string (required), k: integer (default 3),
      data_dir: string (optional, default pole_rag config DATA_DIR)}`, mode `sync`;
      handler calls `pole_rag.query(db_name, query, k, data_dir)` and serializes
      top-k results (text/caption + `source_document` + `image_path`).
- [ ] Import discipline: chatbot imports only `pole_rag` public API (no internal
      modules); linter check.
- [ ] Unit tests: each tool registers with correct name/params; handler returns k=3
      against a Chroma temp dir; unknown/empty DB → `ToolError`; `k` respected.
- [ ] Integration test (marked `integration`): seed a temp DB, call each tool, assert
      results reference expected source documents.

## Dependencies
Phase 4 (CLI + query API) and chatbot ToolRegistry patterns.

## Acceptance Criteria
- Chatbot unit suite green (`pixi run test-chatbot`).
- 4 tools registered in `register_default_tools` output.
- Live integration test queries a seeded temp DB through the tool handlers.
- No `pole-rag` in any `pyproject.toml`.