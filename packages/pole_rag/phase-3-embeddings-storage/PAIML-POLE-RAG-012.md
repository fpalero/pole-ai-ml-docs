# Ticket: PAIML-POLE-RAG-012

## Title
[Infrastructure] Implement shared HuggingFace embeddings (`embeddings.py`)

## Description
Phase 3: single `HuggingFaceEmbeddings` instance using the cached local model
`sentence-transformers/all-MiniLM-L6-v2` (384 dims). Used by ChromaStore for both text
chunks and image captions so distances are comparable.

## What to Do (Implementation Steps)
- [ ] Step 1: Implement `get_embedder()` in `packages/pole_rag/src/pole_rag/embeddings.py`
      returning a cached `HuggingFaceEmbeddings(model_name=EMBED_MODEL,
      model_kwargs={"device": "cpu"})`.
- [ ] Step 2: Add `embed_texts(texts: list[str]) -> list[list[float]]` convenience wrapper.
- [ ] Step 3: Ensure no network download at runtime (model cached; log a clear message if
      the model is missing locally).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] The code compiles/lints without errors.
- [ ] `embed_texts` returns vectors of dimension 384 for non-empty input.
- [ ] Unit tests are written and passing for this specific component (mock embedder).
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-01/UC-05: embedding consistency between seed and query.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-014, PAIML-POLE-RAG-015
- **Blocked By**: PAIML-POLE-RAG-001, PAIML-POLE-RAG-005

## Estimated Effort
- [S]