# Ticket: PAIML-POLE-RAG-005

## Title
[Application] Define central configuration (`config.py`)

## Description
Phase 1: central constants used by extractor, chunker, embeddings, vision, ChromaStore
and CLIs: data dir, embed model, chunk sizes, collection names, Ollama settings, default
k. Keeps magic numbers in one place.

## What to Do (Implementation Steps)
- [ ] Step 1: Implement `packages/pole_rag/src/pole_rag/config.py` with:
      `SOURCES_DIR`, `DATA_DIR`, `EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"`,
      `EMBEDDING_DIM = 384`, `CHUNK_SIZE = 1000`, `CHUNK_OVERLAP = 150`,
      `COLLECTION_TEXT = "text_chunks"`, `COLLECTION_IMAGE = "image_descriptions"`,
      `OLLAMA_MODEL = "llama3.2-vision"`, `OLLAMA_HOST` (env `OLLAMA_HOST`, default
      `http://localhost:11434`), `DEFAULT_K = 3`.
- [ ] Step 2: Expose a `default_data_dir()` helper resolving relative to the package.
- [ ] Step 3: Ensure proper namespace and imports.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] The code compiles/lints without errors.
- [ ] All constants are implemented as specified.
- [ ] Unit tests are written and passing for this specific component.
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-01/UC-05: config values used by seed/query CLIs.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-008, PAIML-POLE-RAG-009, PAIML-POLE-RAG-010, PAIML-POLE-RAG-012, PAIML-POLE-RAG-013, PAIML-POLE-RAG-014, PAIML-POLE-RAG-015
- **Blocked By**: PAIML-POLE-RAG-002

## Estimated Effort
- [S]