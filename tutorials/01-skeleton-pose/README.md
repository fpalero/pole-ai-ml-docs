# 01 — Skeleton Extraction & Pose Processing

> MediaPipe pose extraction done **right**: normalization, biomechanical
> features, and small-data strategies. All grounded in
> `packages/pole_ml/src/pole_ml/processors/skeleton_extractor.py` and friends
> (see `docs/diagrams/pole_ml/`, `docs/diagrams/pole_ml/FLOW.md`).

## Core articles in this theme

| ID | Title | Difficulty | Primary audience |
| :--- | :--- | :--- | :--- |
| A1 | Production-Grade Pose Extraction with MediaPipe | Intermediate | ML/CV |
| A2 | The "Monotonically Increasing Timestamp" Bug | Beginner → Intermediate | All |
| A3 | From Video to Vectors: Biomechanical Feature Engineering | Advanced | ML/CV |
| A4 | Sliding Windows, Data Augmentation & Small Datasets | Intermediate | ML/CV + junior |
| A5 | Automatic Phase Detection in Sports Video | Advanced | ML/CV + instructor |
| A6 | 8-Signal Histogram Analysis & Cohort Z-Scores | Advanced | ML/CV + instructor |

## What makes this theme sellable

- Raw landmarks are useless for classification until normalized; the
  hip-center + shoulder-width normalization is a concrete, reusable recipe.
- Holds a **real bug story** (MediaPipe VIDEO-mode timestamp monotonicity) that
  is high-traffic SEO material.
- Hand-engineered biomechanical features are a counterpoint to
  "throw a transformer at it" — very topical for small dataset problems.

## Source docs

- `docs/diagrams/pole_ml/CLASSES.md`, `docs/diagrams/pole_ml/FLOW.md`
- `docs/packages/pole_ml/project/pole-api-spec.md`, `docs/packages/pole_ml/IMPLEMENTATION_SUMMARY.md`
- `docs/packages/pole_ml/project/Improvements.md` (A5 — timestamp monotonicity)
- `docs/packages/pole_ml/project/retraining-tool-plan.md` (augmentation routes)

---

## Docs per audience

- [`ml-cv.md`](ml-cv.md) — ML / computer vision engineers
- [`fullstack-backend.md`](fullstack-backend.md) — full-stack / backend engineers
- [`junior-mixed.md`](junior-mixed.md) — mixed beginner → intermediate
- [`tech-entrepreneur.md`](tech-entrepreneur.md) — entrepreneur / technical PM