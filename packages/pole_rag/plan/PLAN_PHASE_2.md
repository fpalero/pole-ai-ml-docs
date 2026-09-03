# PLAN PHASE 2 — Marker extraction + atomic table chunking

> **Project:** `pole_rag` · **State:** 📋 PLANNED · **Back to:** [PLAN.md](../PLAN.md)

## Scope
PDF → Markdown + images via Marker (local models), plus the atomic table-preserving
chunker from the user's reference design (regex isolation + preceding-context
injection), with per-PDF error isolation.

## Tasks
- [ ] `extractor.py` — `MarkerExtractor.convert(pdf_path, out_dir) -> (markdown: str, images_dir: Path)`:
      loads Marker models (`load_all_models`), runs `convert_single_pdf`,
      `save_output` to `<out_dir>/<source_stem>/`; per-PDF `try/except` → warn +
      return `None` on failure; empty/unreadable PDF → warning, no crash.
- [ ] `chunker.py` — `chunk_markdown_with_atomic_tables(markdown_text) -> list[str]`:
      `re.compile(r'((?:\|[^\n]*\|(?:\n|$))+)', re.MULTILINE)` split; odd indexes are
      tables → keep atomic; inject up to 3 preceding lines as
      `"--- CONTEXTO DE LA TABLA ---\n..."` prefix; even indexes → plain text via
      `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150,
      separators=["\n\n","\n"," ",""])`.
- [ ] Unit tests: table block stays a single chunk; context prefix present; plain
      paragraphs split; empty input → `[]`; table with separators `|---|---|` variants
      handled; text without tables unaffected.

## Dependencies
Phase 1 (package scaffold + config).

## Acceptance Criteria
- Chunker unit tests green (`pixi run test-rag`).
- A manual smoke on the smallest source PDF yields markdown + images folder
  (integration, real Marker).
- A corrupt/empty PDF produces a warning and does not abort the run.