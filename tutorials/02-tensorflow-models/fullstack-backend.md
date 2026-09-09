# Theme 02 — TensorFlow & Models · Audience: Full-Stack / Backend Engineers

> Backend-focused takes: serving models, browser export pipelines, retraining
> as a service, and turning predictions into stored artifacts.

## Catalog

### B5 (adapted) — Serving a Browser-Exported Model: The Full Pipeline
- **Difficulty:** Intermediate
- **Type:** Integration tutorial
- **Hook:** "The model ships as static files; your job is keeping the browser and the training side in sync."
- **Description:** The tfjs export mechanics from a backend view: int8
  quantization bytes, versioned artifacts per `training_runs.run_id`, and a
  "stale model" flag so the UI knows when a retrain made the shipped model
  obsolete. Backbone of the "model as versioned deliverable" story.
- **Grounding:** `docs/packages/pole_ml/project/pole-api-plan.md`.
- **Sellable angle:** Bridges MLOps and web delivery.

### B6 (adapted) — Predictions → Clips: The Job Pipeline & FFmpeg
- **Difficulty:** Intermediate
- **Type:** Integration tutorial
- **Hook:** "Classification ran in a worker; now ship the clip."
- **Description:** `VideoCutter` as a backend service: windowed detection,
  dual-threshold + debounce, region reconstruction, and the lossless ffmpeg
  `-ss`/`-to` extraction. Emphasizes the job-queue and file-handling side.
- **Grounding:** `docs/packages/pole_ml/video-cutter-integration.md`.
- **Sellable angle:** Concrete "ML in a backend job" pattern.

### B3 (product-aware) — The Hybrid Classifier as an API Contract
- **Difficulty:** Intermediate
- **Type:** Architecture explainer
- **Hook:** "Two classifiers behind one endpoint — and the fallback logic is the interesting part."
- **Description:** The LSTM-first, Chroma-fallback pattern described as an API
  concern: confidence thresholds, fallback semantics, and what the client
  actually receives. Backend teams implementing ML endpoints will resonate.
- **Grounding:** `docs/diagrams/pole_ml/CLASSES.md` (HybridClassifier).
- **Sellable angle:** Positions hybrid patterns for API designers.