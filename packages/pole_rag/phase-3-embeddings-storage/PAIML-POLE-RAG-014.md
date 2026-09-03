# Ticket: PAIML-POLE-RAG-014

## Title
[Infrastructure] Implement ChromaStore (`chroma_store.py`)

## Description
Phase 3: `ChromaStore(output_dir, name)` wraps `chromadb.PersistentClient(path=<output>/<name>)`
with two collections (`text_chunks`, `image_descriptions`) using the shared HF embedder.
`rebuild()` implements full-rebuild semantics (Option C): delete + recreate collections
so no stale entries survive. Also provides `counts()` and `list_sources()` for inspect.

## What to Do (Implementation Steps)
- [ ] Step 1: Implement `ChromaStore` in `packages/pole_rag/src/pole_rag/chroma_store.py`.
- [ ] Step 2: `__init__`: create `PersistentClient(path=str(output_dir / name))`;
      `get_or_create_collection` for both collections with `embedding_function=get_embedder()`.
- [ ] Step 3: `rebuild()`: delete both collections if they exist, recreate them.
- [ ] Step 4: `add_text(chunks, source_doc)` / `add_image(captions, metadatas)` with
      deterministic ids (`{source_stem}_text_{i}` / `{source_stem}_img_{i}`).
- [ ] Step 5: `counts() -> dict[str, int]`, `list_sources() -> list[str]` (distinct
      `source_document`), `query(query_text, k=DEFAULT_K) -> list[dict]` merging both
      collections sorted by distance.
- [ ] Step 6: Add `query` helper on both collections returning metadata + distance.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] The code compiles/lints without errors.
- [ ] `rebuild()` leaves collections empty (no stale entries) — verified by test.
- [ ] `query` returns ≤ k merged results with `source_document` metadata.
- [ ] Unit tests are written and passing for this specific component (temp dir).
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-02 (re-seed): rebuild drops old entries.
- [ ] Run UC-05 (query k=3): merged results with metadata.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-015, PAIML-POLE-RAG-019, PAIML-POLE-RAG-020
- **Blocked By**: PAIML-POLE-RAG-001, PAIML-POLE-RAG-005, PAIML-POLE-RAG-012

## Estimated Effort
- [M]