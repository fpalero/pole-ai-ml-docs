# Ticket: PAIML-POLE-RAG-032

## Title
[Infrastructure] Uninstall Marker (drop `marker-pdf` + Surya weight lane)

## Description
Phase 7, step 1 of 2 (removal only; replacement lands in 033). Evidence:
`pixi run rag-seed` hangs on Marker (`marker-pdf` 2.x, multi-GB Surya models
on CPU) plus `llava:7b` per-image captions over the ~550 MB / 16-PDF corpus.
A scan of the corpus showed **13 TEXT-OK + 3 MIXED, 0 scanned** — every PDF
has embedded text, so PyMuPDF suffices and the Marker/Surya lane is dead
weight. This ticket removes the dependency; extractor tests will fail after
it (known-break, fixed by 033).

## Repository
pole-ai-ml (code + `pixi.toml`/`pixi.lock`; this ticket file itself is
committed to `pole-ai-ml-docs`)

## What to Do (Implementation Steps)
- [ ] Step 1 [pole-ai-ml]: In root `pixi.toml` `[pypi-dependencies]`, remove
      the `marker-pdf = ">=2,<3"` line plus the NOTE comment block above it
      (the 1.x-vs-2.x unsatisfiability note — obsolete once Marker is gone).
      Keep `pillow` (still needed for image handling).
- [ ] Step 2 [pole-ai-ml]: `[activation.env]` HF offline block
      (`HF_HUB_OFFLINE` / `HF_DATASETS_OFFLINE`): remove **only if
      marker-only**. It is NOT marker-only — `sentence-transformers`
      embeddings still resolve via the local HF cache — so KEEP both vars and
      only trim the comment to drop the `marker, surya` mention.
- [ ] Step 3 [pole-ai-ml]: `[constraints]` `websockets = ">=16.1.1,<17"` —
      its comment justifies it solely via `marker-pdf` 2.x → `google-genai`.
      Check whether the solve still needs it after Marker removal; drop it
      only if `pixi install` stays green without it, and record the outcome
      on the ticket either way.
- [ ] Step 4 [pole-ai-ml]: Run `pixi install` to regenerate the lock and
      confirm `marker-pdf` (+ `surya-ocr`) are gone from `pixi.lock`.
- [ ] Step 5 [pole-ai-ml]: Run `pixi run test-rag` — the suite must still
      COLLECT (no import-time crash). Extractor tests (`test_extractor_live`
      and any Marker-mocked extractor tests) MAY FAIL here: record the
      failure list as the known-break fixed by 033. All non-extractor unit
      tests must stay green.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `marker-pdf` absent from `pixi.toml` `[pypi-dependencies]` and from
      `pixi.lock` (no `surya-ocr` either).
- [ ] `HF_HUB_OFFLINE` / `HF_DATASETS_OFFLINE` retained with an updated
      comment (embeddings still need the offline cache).
- [ ] `pixi run test-rag` collects; failures — if any — are limited to
      extractor tests, listed on the ticket as the 033 known-break.
- [ ] No `packages/pole_rag/src/` behaviour change in this ticket (pure
      removal; `extractor.py` still imports Marker lazily so collection
      does not crash).
- [ ] The changes do not break existing non-extractor unit tests
      (regression check).

## Integration Tests to Run (Local Verification)
- [ ] None in this ticket (removal only) — full-corpus text-only seed
      (< 5 min) is the 033 acceptance probe (UC-01 analogue).

## Dependencies
- **Blocks**: PAIML-POLE-RAG-033
- **Blocked By**: —

## Estimated Effort
- [S]
