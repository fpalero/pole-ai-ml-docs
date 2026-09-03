# PLAN PHASE 3 — Embeddings + Chroma multi-collection storage

> **Project:** `pole_rag` · **State:** 📋 PLANNED · **Back to:** [PLAN.md](../PLAN.md)

## Scope
Embed text chunks and Ollama-generated image captions, store into Chroma DB with two
collections per resource DB (`text_chunks`, `image_descriptions`), full-rebuild
semantics, deterministic ids, source-linked metadata.

## Tasks
- [ ] `embeddings.py` — shared `HuggingFaceEmbeddings(model_name=EMBED_MODEL,
      model_kwargs={"device": "cpu"})` singleton (cached local model, no download).
- [ ] `vision.py` — `OllamaVision.describe(image_path) -> str`: `ChatOllama(
      model=OLLAMA_MODEL, base_url=OLLAMA_HOST)` with a caption prompt
      ("A detailed chart, diagram or image showing"); per-image `try/except` → fallback
      caption string; configurable model/host.
- [ ] `chroma_store.py` — `ChromaStore(output_dir, name)`: `chromadb.PersistentClient(
      path=<output_dir>/<name>)`; `get_or_create_collection` for both collections with
      `embedding_function` (same HF model); `rebuild()` = delete + recreate collections
      (full rebuild, Option C); `counts()`, `list_sources()`.
- [ ] `seeder.py` — `seed_resource(input_dir, output_dir, name)`: dedupe PDFs →
      for each PDF: Marker extract → atomic chunk → embed + add to `text_chunks`
      (ids `{source_stem}_text_{i}`, metadata `{source_document, file_name, type:
      "text_or_table"}`); scan `<out>/<stem>/` images → Ollama caption → embed + add
      to `image_descriptions` (ids `{source_stem}_img_{i}`, metadata
      `{source_document, image_path, image_title, type: "image"}`); logs counts.
- [ ] Integration test (marked `integration`): seed the smallest source PDF into a
      **temp** output dir with real Marker + real HF + real Ollama; assert
      `text_chunks.count() > 0` and `image_descriptions.count() > 0`.

## Dependencies
Phase 2 (extractor + chunker).

## Acceptance Criteria
- Unit tests for ChromaStore (rebuild drops old entries; metadata round-trip).
- Live integration seeds one PDF into temp dir and both collections are populated.
- Re-running seed produces deterministic ids and no stale entries.