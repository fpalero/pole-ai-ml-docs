# Ticket: PAIML-POLE-RAG-016

## Title
[Application] Integration test: seed smallest source PDF (real Marker + HF + Ollama)

## Description
Phase 3: live integration test (marked `integration`) that seeds the smallest source PDF
(e.g., `sources/psicology/_OceanofPDF.com_The_Mindful_Athlete_-_George_Mumford.pdf`, ~2.5 MB)
into a temp output dir using **real** Marker, real HuggingFace embeddings and real Ollama
`llama3.2-vision`. Asserts both collections are populated.

## What to Do (Implementation Steps)
- [ ] Step 1: Create `packages/pole_rag/tests/test_seed_live.py` marked `integration`.
- [ ] Step 2: Locate the smallest PDF under `packages/pole_rag/sources/` (by size, skip if no
      sources present).
- [ ] Step 3: Run `seed_resource(input, tmp_path, "test")`.
- [ ] Step 4: Assert `text_chunks.count() > 0` and `image_descriptions.count() > 0`
      (images may be absent for some PDFs — assert text only if so, log image count).
- [ ] Step 5: Run via `pixi run test-rag-live`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Integration test passes locally with real services.
- [ ] Test uses a temp output dir only (never `packages/pole_rag/data/`).
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-01: real seed → both collections > 0.

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLE-RAG-003, PAIML-POLE-RAG-015

## Estimated Effort
- [M]