# 02 — TensorFlow & Model Architecture

> The core ML story: a Sequence-to-Vector LSTM that doubles as an embedder, the
> hybrid classifier, honest evaluation, browser export, and turning predictions
> into action. Grounded in
> `packages/pole-train-model/src/pole_ml/models/video_training.py`.

## Core articles in this theme

| ID | Title | Difficulty | Primary audience |
| :--- | :--- | :--- | :--- |
| B1 | Sequence-to-Vector: LSTM that Outputs Embeddings, Not Just Classes | Advanced | ML/CV |
| B2 | Defensive Training: Leave-One-Out + Categorical Crossentropy | Intermediate | ML/CV |
| B3 | The Hybrid Classifier Pattern: Neural Net + Vector Search Fallback | Intermediate | ML/CV + all |
| B4 | Model Persistence, Versioning & the Retraining Toolkit | Intermediate | ML/CV + backend |
| B5 | Exporting to the Browser: TensorFlow.js + int8 Quantization | Intermediate | Frontend + ML/CV |
| B6 | From Recognition to Action: VideoCutter with Confidence History & Debounce | Intermediate | ML/CV + backend |
| B7 | CLI-First ML Pipeline: Eight Commands, One Workflow | Intermediate | ML/CV + backend |
| B8 | Testing an ML Pipeline Honestly | Intermediate | ML/CV |
| B9 | Human-in-the-Loop Model Promotion | Intermediate | ML/CV + backend |

## What makes this theme sellable

- **B3 is the signature idea** — deep learning with a vector-search fallback is
  genuinely rare in tutorials and broadly redone by teams.
- Dual-purpose bottleneck embeddings (classify + embed) is an under-documented
  trick with huge practical value.
- B5 (tfjs + int8 under 2 MB, <30 ms/frame) taps the very popular
  "run ML in the browser" keyword.
- Rich debugging/MLOps angle: leave-one-out eval, per-class gates, fine-tune vs
  few-shot routes.

## Source docs

- `docs/diagrams/pole_ml/CLASSES.md`, `docs/diagrams/pole_ml/FLOW.md`
- `docs/packages/pole_ml/project/pole-api-plan.md` (tfjs export requirements)
- `docs/packages/pole_ml/project/retraining-tool-plan.md` (pipelines D/E)
- `docs/packages/pole_ml/video-cutter-integration.md` (B6)

---

## Docs per audience

- [`ml-cv.md`](ml-cv.md) — ML / computer vision engineers
- [`fullstack-backend.md`](fullstack-backend.md) — full-stack / backend engineers
- [`junior-mixed.md`](junior-mixed.md) — mixed beginner → intermediate
- [`tech-entrepreneur.md`](tech-entrepreneur.md) — entrepreneur / technical PM