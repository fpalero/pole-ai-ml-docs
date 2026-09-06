# Theme 02 — TensorFlow & Models · Audience: Entrepreneur / Technical PM

> Model strategy without the math: when to trust the model, when to fall back,
> how to budget retraining, and how to ship the model to users at low cost.

## Catalog

### B3 (strategy) — Confidence Is a Product Feature
- **Difficulty:** Any
- **Type:** Strategy explainer
- **Hook:** "Users don't care about accuracy curves; they care that the app is rarely wrong."
- **Description:** The hybrid fallback as a product decision: what a confidence
  threshold means for the user experience, and how the vector-search safety net
  handles "tricks we've never seen" — a core differentiator for a technique-
  coaching product.
- **Grounding:** `docs/diagrams/pole_ml/CLASSES.md`.
- **Sellable angle:** Product-strategy content rarely written by engineers.

### B5 (product lens) — On-Device ML: User Privacy and Zero-Latency as Selling Points
- **Difficulty:** Any
- **Type:** Product/technical explainer
- **Hook:** "A 2 MB model in the browser means no upload, no wait, no privacy question."
- **Description:** The business case for int8 tfjs export: payload < 2 MB, < 30
  ms/frame inference, offline capability, and the versioning story for shipped
  models. Helps founders price and position on-device features.
- **Grounding:** `docs/packages/pole_ml/project/pole-api-plan.md`.
- **Sellable angle:** On-device ML is a hot topic; connects to privacy-as-feature.