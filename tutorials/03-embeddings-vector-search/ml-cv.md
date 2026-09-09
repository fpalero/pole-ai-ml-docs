# Theme 03 — Embeddings & Vector Search · Audience: ML / CV Engineers

> The vector-store companion to the model: generating 128-d embeddings,
> persisting them, and doing k-NN voting — plus a real cautionary tale.

## Catalog

### C1 — ChromaDB in Practice: k-NN Voting & the Config-Bug Case Study
- **Difficulty:** Intermediate
- **Type:** Technical guide + case study
- **Hook:** "Your vector store silently lost data because two files disagreed on a string."
- **Description:** `SkeletonEmbedding` (128-d bottleneck) → ChromaDB
  (`SkeletonRepository`, cosine). Then the cautionary tale: components pointed
  at different persist dirs and collection names (`FeaturesEmbeddings` vs
  `chroma_db`/`chroma_data`, `movement_embeddings` vs `skeleton_vectors`), so
  written data was invisible to classifiers. Teaches canonical config, idempotent
  indexing, and verification tooling.
- **Grounding:** `docs/packages/pole_ml/project/Improvements.md` (B1 — canonical fix `3b46cff`), `docs/diagrams/pole_ml/CLASSES.md`.
- **Sellable angle:** Real "I broke ChromaDB" story — high resonance, low
  redundancy in the tutorial space.

### C2 — Retrieval-Augmented Recognition: Nearest-Neighbor Fallback
- **Difficulty:** Intermediate
- **Type:** Architecture guide
- **Hook:** "When novelty is the norm, nearest-neighbor is your classifier."
- **Description:** `ChromaClassifier` (k-NN voting + confidence) and how it plugs
  under the HybridClassifier as the LSTM fallback. Covers cosine-distance
  thresholds (e.g. < 0.3), metadata hygiene, and returning ranked matches with
  scores.
- **Grounding:** `docs/diagrams/pole_ml/CLASSES.md`, `docs/packages/pole_ml/PLAN.md` (UC-ML-06, `find_by_similarity`).
- **Sellable angle:** The "few-shot-friendly classifier" story you can't get from
  a textbook.