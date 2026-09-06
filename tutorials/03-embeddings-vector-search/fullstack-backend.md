# Theme 03 — Embeddings & Vector Search · Audience: Full-Stack / Backend Engineers

> Vector stores for backend engineers: storage contracts, idempotent indexing,
> and the operational lessons of running ChromaDB in a service.

## Catalog

### C1 (adapted) — Running ChromaDB as a Service: The Config Trap
- **Difficulty:** Intermediate
- **Type:** Operations guide
- **Hook:** "Three services, three paths to the same collection, one silent outage."
- **Description:** The Chroma config inconsistency case study from an ops view:
  why duplication of config strings across packages/scripts breaks data flow,
  and how a single canonical config + `verify_collection`/`get_all_samples`
  tooling prevents it. Includes persist-dir and collection naming as
  first-class API concerns.
- **Grounding:** `docs/packages/pole_ml/project/Improvements.md` (B1).
- **Sellable angle:** "Data integrity in vector stores" is underserved content.

### C2 (adapted) — Exposing Similarity Search Behind an Endpoint
- **Difficulty:** Intermediate
- **Type:** Integration tutorial
- **Hook:** "Give users 'show me something like this' in a weekend."
- **Description:** The `find_by_similarity` pattern: ranked matches with scores,
  k-NN voting, and how to expose it as a clean API/CLI. Strong crossover with
  feature-store and recommendation use cases.
- **Grounding:** `docs/packages/pole_ml/PLAN.md` (UC-ML-06).
- **Sellable angle:** Similarity-search-as-a-service is broadly relevant beyond
  CV.