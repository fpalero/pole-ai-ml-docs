# PAIML-POLE-API-109 — Deterministic RAG image block synthesis

## Summary

RAG tool results (`query_pole`, `query_biomechanics`, `query_calisthenics`, `query_psicology`) lack deterministic block synthesis. When the LLM fails to emit proper `image` blocks from RAG hits, the JSON array ends up as raw text inside an `md` block — the user sees `[{"type": "image", ...}]` instead of rendered images.

Analysis tools (`extract_frames`, `get_coach_pose`) work because they have synthesizers in `_TOOL_SYNTHESIZERS`. RAG tools do not.

## Root Cause

| | Analysis Images (work) | RAG Images (broken) |
|---|---|---|
| In `TOOL_EXPECTED_BLOCKS`? | YES | **NO** |
| In `_TOOL_SYNTHESIZERS`? | YES | **NO** |
| Block synthesis from tool result? | YES, deterministic | **NO — relies 100% on LLM** |
| Tool result provides served URL? | YES (`/api/analyst-artifacts/...`) | **NO — raw filesystem path** |

## Scope

**Backend only** (`app/pole_api/src/analyst_chatbot/answer_shaping.py`).

### Task 1: Register RAG tools in `TOOL_EXPECTED_BLOCKS`

Add all 4 RAG tool names to the map:

```python
"query_pole": ("image",),
"query_biomechanics": ("image",),
"query_calisthenics": ("image",),
"query_psicology": ("image",),
```

### Task 2: Create `_blocks_for_rag_image()` synthesizer

New function that:
1. Reads `results` from the tool result dict (list of hits)
2. For each hit with a non-empty `image_path`:
   - Calls `image_registry.ensure_image_url(hit["image_path"])` to convert raw path → `/api/images/<hash>` URL
   - If the URL is valid (not `None`), builds `{"type": "image", "src": url, "caption": hit.get("image_title"), "source_document": hit.get("source_document")}`
3. Returns the list of image blocks

Key reuse: `ensure_image_url()` already handles all path formats (`data/_OceanofPDF.../file.png`, absolute paths, etc.) — no need to reimplement path logic.

### Task 3: Register synthesizer in `_TOOL_SYNTHESIZERS`

```python
"query_pole": _blocks_for_rag_image,
"query_biomechanics": _blocks_for_rag_image,
"query_calisthenics": _blocks_for_rag_image,
"query_psicology": _blocks_for_rag_image,
```

### Task 4: Unit tests

Test cases:
- RAG result with valid `image_path` → proper `image` block with hash URL
- RAG result with `image_path` pointing to non-existent file → block still created (deterministic URL, 404 at serve time is fine)
- RAG result with empty/missing `image_path` → no block (skip hit)
- RAG result with `image_title` and `source_document` → caption and source populated
- RAG result with no `image_title` → no caption field
- All 4 RAG tool names produce blocks via `blocks_for_tool_call()`
- `ensure_tool_blocks()` appends RAG image blocks when not already present

## Acceptance Criteria

- [ ] `blocks_for_tool_call("query_pole", result_with_images)` returns list of `image` blocks
- [ ] Each block has `src` as `/api/images/<32-hex>` URL (not raw filesystem path)
- [ ] `ensure_tool_blocks()` adds RAG image blocks for all 4 RAG tools
- [ ] Unit tests pass: `pixi run test-api -k rag_image`
- [ ] Existing tests still pass (no regression)

## Blocked By

— (none)

## Blocks

— (none)

## Evidence

Before fix: chat bubble shows `[{"type": "image", "src": "/api/images/0142-07", ...}]` as raw text.
After fix: chat bubble renders `<figure class="rag-image-card">` with `<img>` element.
