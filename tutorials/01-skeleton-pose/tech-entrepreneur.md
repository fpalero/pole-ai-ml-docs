# Theme 01 — Skeleton & Pose · Audience: Entrepreneur / Technical PM

> Non-implementation content: what pose data enables, why normalization is a
> product decision, and how the pipeline maps to user value.

## Catalog

### A1 (product lens) — Why "Just Use MediaPipe" Isn't a Product
- **Difficulty:** Any
- **Type:** Product/technical explainer
- **Hook:** "Raw pose landmarks are a feature, not a product — the gap between them is the engineering moat."
- **Description:** The translation/scale normalization story told as a product
  decision: position/size invariance is what allows one model to serve every
  user. Ideal for founders scoping a sports-tech or fitness-tech product.
- **Grounding:** `docs/diagrams/pole_ml/CLASSES.md`.
- **Sellable angle:** Founders' literature; cross-link to the swing/technique
  analysis niche.

### A4 (product lens) — Data Strategy for a From-Scratch ML Product
- **Difficulty:** Any
- **Type:** Strategy guide
- **Hook:** "You can launch with a few hundred labeled samples if the pipeline is built right."
- **Description:** The augmentation + class-weight + oversampling playbook
  explained at a strategy level: what it costs, what it buys, and when to
  graduate to more data.
- **Grounding:** `docs/packages/pole_ml/project/retraining-tool-plan.md`.
- **Sellable angle:** Pairs with the ML/CV version; aimed at founders budgeting
  data acquisition.