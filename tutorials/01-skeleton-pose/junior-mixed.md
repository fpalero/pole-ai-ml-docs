# Theme 01 — Skeleton & Pose · Audience: Mixed Beginner → Intermediate

> Gentle, end-to-end content that teaches the product build while carrying the
> reader through pose extraction for the first time.

## Catalog

### A2 — The "Monotonically Increasing Timestamp" Bug
- **Difficulty:** Beginner-appropriate
- **Type:** Debugging story
- **Hook:** "Your very first MediaPipe run crashed — here's the fix and why it happened."
- **Description:** A friendly walkthrough of the timestamp bug: what VIDEO mode
  expects, what `reset()` does, and why per-video instances matter. Minimal
  jargon; great first read.
- **Grounding:** `docs/packages/pole_ml/project/Improvements.md` (A5).
- **Sellable angle:** Entry-level SEO article and series gate.

### A1 (adapted) — Pose → Normalized Landmarks, Explained Simply
- **Difficulty:** Beginner
- **Type:** Tutorial
- **Hook:** "Why the same move filmed from two angles looks different to a model — and the fix."
- **Description:** Intuitive explanation of translation/scale invariance with
  the hip-center + shoulder-width normalization, before any code. Shows why
  normalization is the difference between a toy and a product.
- **Grounding:** `docs/diagrams/pole_ml/CLASSES.md`.
- **Sellable angle:** Concept-first tutorial that pre-sells the advanced series.