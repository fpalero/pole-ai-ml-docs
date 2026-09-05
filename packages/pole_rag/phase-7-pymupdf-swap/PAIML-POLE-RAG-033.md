# Ticket: PAIML-POLE-RAG-033

## Title
[Infrastructure] PyMuPDF extractor (`fitz_extractor` + `POLE_RAG_EXTRACTOR` switch + `--skip-images`)

## Description
Phase 7, step 2 of 2 (replacement; fixes the 032 known-break). Replace
Marker with `pymupdf` + `pymupdf4llm` for deterministic text→Markdown
extraction; keep `OllamaVision` (`llava:7b`) only for figures, bypassable
behind `--skip-images`. Corpus evidence (13 TEXT-OK + 3 MIXED, 0 scanned)
means embedded-text extraction covers the full corpus without Surya OCR.

## Repository
pole-ai-ml (code + `pixi.toml`; this ticket file itself is committed to
`pole-ai-ml-docs`)

## What to Do (Implementation Steps)
- [ ] Step 1 [pole-ai-ml]: Add `pymupdf` + `pymupdf4llm` to root `pixi.toml`
      `[pypi-dependencies]` (pinned ranges, same style as `pillow`); run
      `pixi install` and confirm both in `pixi.lock`.
- [ ] Step 2 [pole-ai-ml]: New `packages/pole_rag/src/pole_rag/fitz_extractor.py`
      with the SAME observable contract as `MarkerExtractor.convert`:
      `convert(pdf_path, out_dir) -> (markdown_text, images_dir) | None`.
      Implementation: `pymupdf4llm.to_markdown(pdf, page_chunks=True,
      write_images=True)` writing one `<stem>/` folder per PDF under
      `out_dir` (`<stem>.md` + images); missing/empty/unreadable PDF →
      `None` plus a warning naming the file (mirror `extractor.py` UC-04
      isolation so `extract_all`-style callers keep warn-and-continue).
- [ ] Step 3 [pole-ai-ml]: `packages/pole_rag/src/pole_rag/config.py` — new
      `POLE_RAG_EXTRACTOR` env var (`pymupdf` | `marker`, default `pymupdf`)
      plus an `EXTRACTOR` constant; leave `EMBED_MODEL`, chunk sizes,
      collection names, `OLLAMA_*`, `DEFAULT_K=3` unchanged.
- [ ] Step 4 [pole-ai-ml]: `packages/pole_rag/src/pole_rag/extractor.py` —
      dispatch on the switch with fallback: try the selected backend first;
      on `ImportError`/failure fall back to the other with a warning. The
      `marker` path stays import-lazy (032 removed the dep), so selecting it
      without `marker-pdf` installed warns and falls back to `pymupdf`
      instead of crashing collection.
- [ ] Step 5 [pole-ai-ml]: `cli/seed.py` (and `cli/reseed.py` if it shares
      the parser via `cli/_common.py`) — add a `--skip-images` flag that
      bypasses the `OllamaVision` caption pass entirely (text-only seed).
- [ ] Step 6 [pole-ai-ml]: Thread both knobs through `seeder.py`
      (`skip_images`, extractor selection); keep deterministic ids
      (`{stem}_text_{i}` / `_img_{i}`), UC-04 skip semantics, and per-PDF
      progress logging — add a per-page progress log line during extraction.
- [ ] Step 7 [pole-ai-ml]: Update extractor tests
      (`packages/pole_rag/tests/test_extractor*.py`): mock at the
      `fitz`/`pymupdf4llm` boundary with `tmp_path` (missing/empty/corrupt →
      `None`; valid PDF → `(markdown, images_dir)`); env-switch tests
      (`POLE_RAG_EXTRACTOR` set/unset/invalid); `--skip-images` test asserting
      zero vision calls. Run `pixi run test-rag` GREEN (closes the 032
      known-break).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Text-only seed (`--skip-images`) of the FULL corpus completes in
      < 5 min on the dev machine (no Surya weights, no Ollama calls).
- [ ] Produced Markdown contains `|` tables (atomic-table chunker input
      intact); images land in per-PDF `images_dir` when not skipped.
- [ ] `--skip-images` performs zero `OllamaVision` calls (asserted by test).
- [ ] `POLE_RAG_EXTRACTOR=marker` without `marker-pdf` installed warns and
      falls back to `pymupdf` (no crash, no collection break).
- [ ] `pixi run test-rag` green, including the 032 known-break tests.
- [ ] The changes do not break existing non-extractor unit tests
      (regression check).

## Integration Tests to Run (Local Verification)
- [ ] UC-01 analogue: full-corpus text-only seed → Chroma `text_chunks` > 0,
      < 5 min wall clock.
- [ ] UC-04 analogue: folder with 1 corrupt + 1 valid PDF → valid indexed,
      corrupt skipped with warning, exit 0.

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLE-RAG-032

## Estimated Effort
- [M]
