# Ticket: PAIML-POLE-RAG-015

## Title
[Application] Implement seeder orchestration (`seeder.py`)

## Description
Phase 3: `seed_resource(input_dir, output_dir, name)` wires dedupe → Marker extraction →
atomic chunking → text embeddings → Chroma text collection, plus image scan → Ollama
captions → image embeddings → image collection. This is the heart of UC-01/UC-02.

## What to Do (Implementation Steps)
- [ ] Step 1: Implement `seed_resource(input_dir: Path, output_dir: Path, name: str) ->
      SeedResult` in `packages/pole_rag/src/pole_rag/seeder.py`.
- [ ] Step 2: Call `dedupe_pdfs(input_dir)`; if no PDFs remain, log "no PDFs found" and
      return an empty result (no crash — UC-04).
- [ ] Step 3: For each PDF: `MarkerExtractor.convert` (skip on `None`), chunk with
      `chunk_markdown_with_atomic_tables`, `store.add_text(chunks, source_doc)`.
- [ ] Step 4: For each extracted images dir: collect `.png/.jpg/.jpeg`, `OllamaVision.
      describe_many`, `store.add_image` with metadata `{source_document, image_path,
      image_title, type: "image"}`.
- [ ] Step 5: Use `ChromaStore.rebuild()` before seeding (full rebuild).
- [ ] Step 6: Log per-PDF progress + final counts; return counts in `SeedResult`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] The code compiles/lints without errors.
- [ ] Empty/corrupt inputs handled without crashing (UC-04).
- [ ] Duplicates deduplicated before extraction (UC-03).
- [ ] Unit tests are written and passing for this specific component (mock extractor/
      chunker/store).
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-01: seed `pole` folder → both collections > 0.
- [ ] Run UC-02: re-seed rebuilds without stale docs.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-016, PAIML-POLE-RAG-017, PAIML-POLE-RAG-018
- **Blocked By**: PAIML-POLE-RAG-004, PAIML-POLE-RAG-005, PAIML-POLE-RAG-009, PAIML-POLE-RAG-010, PAIML-POLE-RAG-012, PAIML-POLE-RAG-013, PAIML-POLE-RAG-014

## Estimated Effort
- [L]