# PLAN PHASE 7 — PyMuPDF swap (drop Marker, deterministic text extraction)

> **Project:** `pole_rag` · **State:** 📋 PLANNED ·
> **Back to:** [PLAN.md](../PLAN.md)

## Scope

Replace the Marker extraction lane (`marker-pdf` 2.x + multi-GB Surya
weights) with `pymupdf` + `pymupdf4llm` deterministic text→Markdown, and make
the `llava:7b` figure-caption pass optional behind `--skip-images`. No
collection/schema changes, no CLI renames, no chatbot-tool changes — the
`convert(pdf_path, out_dir) -> (markdown_text, images_dir) | None` contract
is preserved, so chunker → embeddings → Chroma → query are untouched.

How to use this plan (Diátaxis: how-to guide — you are swapping an
extraction backend, not learning RAG concepts):

- If you want the *why* behind dropping Marker, read **Decision record**
  below first, then follow **Tasks** in ticket order 032 → 033.
- If you want facts while working (file paths, env names, contract), use the
  **Reference** boxes inside each ticket — they describe, they do not instruct.

## Evidence (why this phase exists)

- `pixi run rag-seed` hangs: Marker 2.x loads multi-GB Surya models on CPU,
  then `llava:7b` captions every extracted image — over ~550 MB / 16 PDFs
  this never finishes on the dev machine.
- Corpus scan: **13 TEXT-OK + 3 MIXED, 0 scanned** — every source PDF carries
  embedded text. OCR (Surya) buys nothing; a text extractor suffices.
- Branch `feature/PAIML-POLE-RAG-031-base-hash` (base/hash groundwork) merged
  without a ticket file; 032/033 continue the numbering to avoid collision.

## Decision record — why Marker was dropped

**Status:** Accepted · **Date:** 2026-09-04 · **Deciders:** pole_rag
maintainers (doc agent, Phase 7 planning).

**Context:** `pole_rag` extracted PDFs via Marker (`marker-pdf >=2,<3`,
`PdfConverter` + `text_from_rendered` + `save_output` in
`packages/pole_rag/src/pole_rag/extractor.py`), which requires multi-GB
Surya OCR weights on CPU plus a per-image `llava:7b` caption pass
(`OllamaVision`). Seeding the full 16-PDF / ~550 MB corpus hangs. A scan
showed 13 TEXT-OK + 3 MIXED, 0 scanned PDFs — all content is embedded text.

**Decision:** Replace Marker with `pymupdf` + `pymupdf4llm`
(`to_markdown(..., page_chunks=True, write_images=True)`) behind the same
`convert` contract; add a `POLE_RAG_EXTRACTOR=pymupdf|marker` switch with
fallback; gate the vision pass behind `--skip-images`; remove `marker-pdf`
from `pixi.toml`.

**Alternatives considered:**

- *Keep Marker, seed per-PDF with retries* — rejected: Surya-on-CPU cost is
  structural, not transient; every future corpus addition re-pays it.
- *Marker with Surya disabled / text-only mode* — rejected: still drags the
  `marker-pdf` + `google-genai` + `websockets<17` solve weight for zero OCR
  benefit on a 0-scanned corpus.
- *pypdf / pdfminer instead of pymupdf4llm* — rejected: they yield raw text,
  losing the Markdown tables the atomic-table chunker depends on;
  `pymupdf4llm` preserves `|` tables deterministically.

**Consequences:**

- `pixi install` no longer fetches `marker-pdf`/`surya-ocr` (GBs saved);
  the `websockets<17` constraint may become droppable (ticket 032 verifies).
- `HF_HUB_OFFLINE` stays — `sentence-transformers` embeddings still use the
  local HF cache.
- `OllamaVision` (`llava:7b`) remains for figures, but text-only seeding no
  longer needs Ollama running.
- `extractor.py` keeps a lazy `marker` fallback path so the
  `POLE_RAG_EXTRACTOR` switch never crashes collection when `marker-pdf`
  is absent.

## Tasks

- [ ] Ticket 032 — uninstall Marker: remove `marker-pdf` from
      `pixi.toml` `[pypi-dependencies]`, trim (don't drop) the HF offline
      block, re-verify the `websockets` constraint, `pixi install` to
      regenerate the lock, `pixi run test-rag` still collects (extractor
      failures = known-break). Repo `pole-ai-ml`.
- [ ] Ticket 033 — new `src/pole_rag/fitz_extractor.py` (same `convert`
      contract, `page_chunks` + `write_images`), `POLE_RAG_EXTRACTOR`
      switch in `config.py` + `extractor.py` fallback, `--skip-images` on
      the seed CLI, per-page progress log, updated extractor tests.
      Repo `pole-ai-ml`.

Ticket order: 032 → 033 (linear; 033 is blocked by 032).

## Dependencies

- Phase 2 (`extractor.py` contract, `MarkerExtractor.convert` semantics) —
  the contract 033 must preserve.
- Phase 4 (`cli/seed.py`, `cli/_common.py` parser layout) — where
  `--skip-images` lands.
- Ticket 031 groundwork (`feature/PAIML-POLE-RAG-031-base-hash`, merged, no
  ticket file) — base/hash behaviour must keep working through the swap.

## Acceptance Criteria

- Text-only seed (`--skip-images`) of the FULL corpus completes in < 5 min
  on the dev machine.
- Produced Markdown contains `|` tables (atomic-table chunker input intact).
- Images are extracted to per-PDF `images_dir` when not skipped.
- `--skip-images` performs zero `OllamaVision` calls and needs no running
  Ollama instance.
- `pixi run test-rag` green after 033 (032 known-break closed).

## Risks and Mitigations

- **Risk:** `pymupdf4llm` table output differs subtly from Marker's and the
  atomic-table regex misses a variant. **Mitigation:** 033 acceptance
  asserts `|` tables in output; chunker unit tests (multiple separator
  formats) run unchanged against the new Markdown.
- **Risk:** the 3 MIXED PDFs contain scanned pages whose text PyMuPDF can't
  see. **Mitigation:** per-PDF warn-and-continue already isolates them
  (UC-04); vision captions still cover their figures; residual text loss is
  quantified in the 033 verification run.
- **Risk:** dropping the `websockets` constraint breaks an unrelated solve
  (`stagehand` floor `>=16.1.1`). **Mitigation:** 032 drops it only if the
  solve stays green, and records the outcome either way.
