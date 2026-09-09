# Ticket: PAIML-POLE-RAG-035

## Title
[Build/Image] Bake embedder lane into pole-api base image

## Description
Phase 6 staging-ship follow-up (blocker A). Phase 6 staging upload is landed:
4 Chroma DBs + image folders copied from `packages/pole_rag/data/` to
`/data/rag` on the ipsf-server staging pod with on-pod counts matching local
baselines (pole 1720 text + 1806 images, calisthenics 1776 + 972,
biomechanics 4711 + 1610, psychology 4365 + 1633); `/data/chroma` untouched.
The deployed pole-api base image cannot query: `pole_rag.query` crashes with
`ModuleNotFoundError` because `langchain_huggingface` + `sentence_transformers`
live only in the root `pixi.toml` and were never added to
`app/pole_api/docker/base.Dockerfile`. Recorded decision: bake lane (bake both
packages + pre-cached `all-MiniLM-L6-v2` weights into the base image), not the
`HF_HOME`-on-PVC lane from ticket 029 step 5.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Step 1 [pole-ai-ml]: In `app/pole_api/docker/base.Dockerfile`, add
      `langchain-huggingface>=1,<2` + `sentence-transformers>=5.2,<6` to the
      pip install list (pin the same floor/ceiling the seeder uses locally).
- [ ] Step 2 [pole-ai-ml]: Pre-download
      `sentence-transformers/all-MiniLM-L6-v2` at build time into a cache path
      that survives into the production stage (e.g. `HF_HOME` under `/opt/venv`)
      so query time is offline-safe (no first-query network pull on staging).
- [ ] Step 3 [pole-ai-ml]: Rebuild base (new content hash) + thin image;
      verify in-image
      `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"`
      passes with no network.
- [ ] Step 4 [pole-ai-ml]: No `/data/chroma` changes (movement-embeddings
      store stays untouched; this ticket only changes the image).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] In-image offline one-liner green (weights resolve from baked cache, no
      network).
- [ ] `import pole_chatbot.rag_tools` works inside the rolled image.
- [ ] Missing-DB still maps to `ToolError` (safe-unknown contract unchanged).
- [ ] Existing unit tests green (rag + chatbot suites, no regressions).

## Integration Tests to Run (Local Verification)
- [ ] In-image offline embedder one-liner (see Step 3) with network disabled.
- [ ] `pixi run test-rag` + `pixi run test-chatbot` green before ship.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-030
- **Blocked By**: —
  (independent, parallel with PAIML-POLE-RAG-036 — no ordering constraint)

## Estimated Effort
- [M]
