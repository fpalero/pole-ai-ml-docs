# Theme 02 — TensorFlow & Models · Audience: Mixed Beginner → Intermediate

> The gentlest entry to LSTM + embeddings: concept-first, with the deep-dives
> clearly signposted for later.

## Catalog

### B3 (intro) — Why a Model Sometimes Needs a "Second Opinion"
- **Difficulty:** Beginner
- **Type:** Concept explainer
- **Hook:** "A neural net can be confidently wrong — here's how we give it a safety net."
- **Description:** The hybrid classifier at a conceptual level: model first,
  similarity-search fallback when confidence is low. No dense math; just the
  intuition and a diagram.
- **Grounding:** `docs/diagrams/pole_ml/CLASSES.md`.
- **Sellable angle:** Funnel piece that funnels up to the B3 deep-dive.

### B2 (intro) — Testing a Model Honestly When Data Is Scarce
- **Difficulty:** Beginner
- **Type:** Tutorial
- **Hook:** "Your accuracy number can lie — leave-one-out won't."
- **Description:** A gentle explanation of Leave-One-Out evaluation, accuracy vs
  per-class metrics, and why you should gate a release on both. Concrete but
  approachable.
- **Grounding:** `docs/diagrams/pole_ml/CLASSES.md` (ModelEvaluator).
- **Sellable angle:** Accessible evaluation literacy — broad appeal.

### B1 (intro) — What Even Is an "Embedding"? (With a Real LSTM Example)
- **Difficulty:** Beginner → Intermediate
- **Type:** Explainer + demo
- **Hook:** "An embedding is just a number sentence for your data — here's one doing double duty."
- **Description:** Intuitive intro to embeddings via the LSTM bottleneck: why a
  128-d vector from the middle of the network is useful for both classifying and
  searching. Sets up the full series.
- **Grounding:** `docs/packages/pole_ml/IMPLEMENTATION_SUMMARY.md`.
- **Sellable angle:** High-demand "what is an embedding" keyword with a unique,
  concrete example.