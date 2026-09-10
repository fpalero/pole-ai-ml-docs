# 03 — Embeddings & Vector Search

> 128-d embeddings from the LSTM bottleneck, ChromaDB storage, k-NN voting,
> and retrieval-augmented recognition for low-confidence cases. Grounded in
> `packages/pole-train-model/src/pole_ml/classifiers/chroma_classifier.py`.

## Core articles in this theme

| ID | Title | Difficulty | Primary audience |
| :--- | :--- | :--- | :--- |
| C1 | ChromaDB in Practice: k-NN Voting & the Config-Bug Case Study | Intermediate | ML/CV + backend |
| C2 | Retrieval-Augmented Recognition: Nearest-Neighbor Fallback | Intermediate | ML/CV |

## What makes this theme sellable

- **C1 carries a real cautionary tale:** components disagreed on persist dir and
  collection name, silently making written data invisible to classifiers
  (documented in `docs/packages/pole_ml/project/Improvements.md` B1). A great
  "how to hurt yourself with vector stores" lesson everyone can relate to.
- Cosine-distance thresholds, k-NN voting with confidence, and idempotent
  indexing are practical, reusable patterns.
- Sits right on the retrieval-augmented generation / RAG wave.

## Source docs

- `docs/diagrams/pole_ml/CLASSES.md` (SkeletonEmbedding, ChromaClassifier, HybridClassifier)
- `docs/packages/pole_ml/project/Improvements.md` (B1 config inconsistency)
- `docs/packages/pole_ml/PLAN.md` (UC-ML-06 embeddings + similarity)

---

## Docs per audience

- [`ml-cv.md`](ml-cv.md) — ML / computer vision engineers
- [`fullstack-backend.md`](fullstack-backend.md) — full-stack / backend engineers
- [`junior-mixed.md`](junior-mixed.md) — mixed beginner → intermediate
- [`tech-entrepreneur.md`](tech-entrepreneur.md) — entrepreneur / technical PM