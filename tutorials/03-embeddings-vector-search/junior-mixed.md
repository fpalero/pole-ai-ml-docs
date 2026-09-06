# Theme 03 — Embeddings & Vector Search · Audience: Mixed Beginner → Intermediate

> Friendly entry to vector stores: what an embedding is for practical purposes,
> and the "search by meaning" intuition, grounded in a real project already.

## Catalog

### C2 (intro) — "Show Me Something Like This": Your First Similarity Search
- **Difficulty:** Beginner
- **Type:** Tutorial
- **Hook:** "If you can turn anything into a vector, you can search for anything by resemblance."
- **Description:** A conceptual + hands-on intro: generate embeddings from a
  model, store them in ChromaDB, rank by cosine distance. Uses the project's
  trick-embedding example end to end.
- **Grounding:** `docs/packages/pole_ml/PLAN.md` (UC-ML-06).
- **Sellable angle:** On-ramp to the whole vector/embedding topic.

### C1 (intro) — The Day My Vector Database "Lost" Data
- **Difficulty:** Beginner
- **Type:** Debugging story
- **Hook:** "I wrote vectors successfully and my classifier found nothing — behold the config."
- **Description:** The config-bug cautionary tale without the noise: two
  collection names, data written to one, read from the other. A perfect
  beginner lesson on why "works on my machine" config must be teleported.
- **Grounding:** `docs/packages/pole_ml/project/Improvements.md` (B1).
- **Sellable angle:** Engaging bug story teaches a durable lesson.