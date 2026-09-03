# Ticket: PAIML-POLE-RAG-009

## Title
[Infrastructure] Implement Marker PDF extractor (`extractor.py`)

## Description
Phase 2: `MarkerExtractor` wraps Marker to convert a PDF into Markdown + an images
folder using locally cached models (no downloads). Per-PDF error isolation: a corrupt,
unreadable, or empty PDF must not abort the whole seed run.

## What to Do (Implementation Steps)
- [ ] Step 1: Implement `MarkerExtractor` in `packages/pole_rag/src/pole_rag/extractor.py`.
- [ ] Step 2: `convert(pdf_path: Path, out_dir: Path) -> tuple[str, Path] | None`:
      load Marker models (`load_all_models`), run `convert_single_pdf(pdf_path, models,
      max_pages=None)`, `save_output(full_text, images, out_metadata,
      out_dir / source_stem)`.
- [ ] Step 3: Wrap the whole conversion in `try/except`; on failure log a warning with
      the PDF name and return `None` (warn-and-continue).
- [ ] Step 4: Return `(markdown_text, images_dir)`; images dir may be empty/missing.
- [ ] Step 5: Add a module-level `extract_all(pdf_files, out_dir)` helper iterating files
      and collecting failures.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] The code compiles/lints without errors.
- [ ] All defined methods are implemented as specified.
- [ ] A corrupt/empty PDF returns `None` + warning; valid PDFs still processed.
- [ ] Unit tests are written and passing for this specific component (mock/real split).
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-04 (unreadable PDF): a corrupt PDF is skipped with warning, valid PDF indexed.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-015, PAIML-POLE-RAG-016
- **Blocked By**: PAIML-POLE-RAG-001, PAIML-POLE-RAG-002, PAIML-POLE-RAG-005

## Estimated Effort
- [M]