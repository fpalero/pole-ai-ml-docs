# Ticket: PAIML-POLE-RAG-037

## Title
[Image] Fix base-image runner disk-full (CPU-only torch)

## Description
Phase 6 staging-ship follow-up to PAIML-POLE-RAG-035 (embedder bake lane).
The 035 bake added `langchain-huggingface>=1,<2` +
`sentence-transformers>=5.2,<6` to `app/pole_api/docker/base.Dockerfile`,
which pulls the default CUDA `torch` (~2.5 GB) on top of an already
TensorFlow-heavy image. The `base` job in
`.github/workflows/build-push.yml` now fails on GitHub-hosted runners with
`No space left on device` (`#23 ... [Errno 28] No space left on device` at
the `pip install` step; two retries confirmed identical failure). This
blocks PAIML-POLE-RAG-030's completion — 030's embedder proof can proceed
only once a baked image builds.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Step 1 [pole-ai-ml]: In `app/pole_api/docker/base.Dockerfile`,
      install the HF embedder lane CPU-only — `pip install torch
      --index-url https://download.pytorch.org/whl/cpu` (or
      `--extra-index-url` carefully scoped) BEFORE `sentence-transformers`,
      OR pin `sentence-transformers` + torch CPU wheels in the same RUN with
      a controlled index so the default CUDA torch (~2.5 GB) never lands.
- [ ] Step 2 [pole-ai-ml]: Keep `langchain-huggingface>=1,<2` +
      `sentence-transformers>=5.2,<6` (merged in 035) — embeddings remain
      bit-identical, NO model change, NO reseeding of the Chroma DBs seeded
      with `sentence-transformers/all-MiniLM-L6-v2`.
- [ ] Step 3 [pole-ai-ml]: Keep the 035 `HF_HOME` pre-download of
      `all-MiniLM-L6-v2` + `HF_HUB_OFFLINE=1` behavior unchanged.
- [ ] Step 4 [pole-ai-ml]: Verify the `base` job in
      `.github/workflows/build-push.yml` succeeds on a GitHub-hosted runner
      (runner has ~14 GB; CUDA torch pushed it over; CPU torch must fit).
- [ ] Step 5 [pole-ai-ml]: Do NOT touch `packages/pole_rag` python code, do
      NOT change the embedder class, do NOT reseed `/data/rag`.

## Why CPU-torch now (not ONNX/fastembed)
Lowest risk (identical vectors, no re-embed), smallest diff. CPU-only torch
produces bit-identical `all-MiniLM-L6-v2` embeddings — the Chroma DBs stay
valid with zero reseeding. ONNX/fastembed is a possible future size
optimization, explicitly out of scope here.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `base` build passes on a GitHub-hosted runner.
- [ ] Baked image contains `sentence-transformers` + `langchain-huggingface`
      and the MiniLM weights (035 offline one-liner still green).
- [ ] 030's embedder proof can proceed.
- [ ] Existing unit tests green (rag + chatbot suites, no regressions).

## Integration Tests to Run (Local Verification)
- [ ] `base` job green in `build-push.yml` on a hosted runner.
- [ ] In-image offline embedder one-liner (035 Step 3) with network disabled.
- [ ] `pixi run test-rag` + `pixi run test-chatbot` green before ship.

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLE-RAG-035

## Estimated Effort
- [S]
