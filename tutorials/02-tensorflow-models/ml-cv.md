# Theme 02 — TensorFlow & Models · Audience: ML / CV Engineers

> The flagship ML content. Deep coverage of the architecture, the evaluation
> discipline, the hybrid fallback, and the deployment-to-browser story.

## Catalog

### B1 — Sequence-to-Vector: LSTM that Outputs Embeddings, Not Just Classes
- **Difficulty:** Advanced
- **Type:** Architectural deep-dive
- **Hook:** "One forward pass gives you logits AND an embedding — here's the bottleneck trick."
- **Description:** `VideoTraining` (Sequence-to-Vector): how a classification
  LSTM exposes its bottleneck layer so one model serves both tasks —
  classification logits and similarity-search embeddings (128-d). Covers the
  input contract (30×14 windows) and why the dual output beats training two models.
- **Grounding:** `docs/diagrams/pole_ml/CLASSES.md` (VideoTraining),
  `docs/packages/pole_ml/IMPLEMENTATION_SUMMARY.md`.
- **Sellable angle:** Under-documented, high-value pattern; position as the
  "one model, two jobs" piece.

### B2 — Defensive Training: Leave-One-Out + Categorical Crossentropy
- **Difficulty:** Intermediate
- **Type:** Technical guide
- **Hook:** "Train on tiny labeled datasets without fooling yourself."
- **Description:** `ModelTrainer`/`ModelEvaluator` in detail: Leave-One-Out
  splits, early stopping + LR scheduling, per-class metrics as a release gate,
  and how to decide a run is "good enough".
- **Grounding:** `docs/packages/pole_ml/project/pole-api-plan.md`,
  `docs/diagrams/pole_ml/CLASSES.md`.
- **Sellable angle:** Honest-evaluation content resonates across small-data ML.

### B3 — The Hybrid Classifier Pattern: Neural Net + Vector Search Fallback ⭐
- **Difficulty:** Intermediate
- **Type:** Architecture guide
- **Hook:** "When the LSTM isn't sure, the vector store speaks up — and accuracy goes up."
- **Description:** The signature pattern. LSTM classifies first; below a
  confidence threshold (0.7) a ChromaDB k-NN fallback rescues low-confidence and
  novel classes. Implementation, thresholds, tuning.
- **Grounding:** `docs/diagrams/pole_ml/CLASSES.md` (HybridClassifier, LstmClassifier, ChromaClassifier).
- **Sellable angle:** THE differentiator — unique, immediately reusable, cited
  by the launch pack.

### B4 — Model Persistence, Versioning & the Retraining Toolkit
- **Difficulty:** Intermediate
- **Type:** Guide (MLOps-lite)
- **Hook:** "Your model is a data artifact — version it like one."
- **Description:** `ModelPersistence` (.keras/SavedModel + metadata), and the
  retraining routes compared: fine-tune existing, few-shot assist, threshold
  steering, and when to retrain from scratch.
- **Grounding:** `docs/packages/pole_ml/project/retraining-tool-plan.md` (Pipelines D/E), `docs/diagrams/pole_ml/CLASSES.md`.
- **Sellable angle:** "MLOps for a one-dev team" - every indie ML dev's reality.

### B5 — Exporting to the Browser: TensorFlow.js + int8 Quantization
- **Difficulty:** Intermediate
- **Type:** Tutorial
- **Hook:** "2.8 MB to under 2 MB and 30 ms/frame — the tfjs export recipe."
- **Description:** Convert the `.keras` model to a TensorFlow.js LayersModel via
  `tensorflowjs_converter --quantization_bytes 1` (int8 weights); version model
  artifacts by run_id; rebuild the exact training-time input window in the
  browser before inference.
- **Grounding:** `docs/packages/pole_ml/project/pole-api-plan.md` (frontend model export).
- **Sellable angle:** Huge "ML in the browser" keyword demand.

### B6 — From Recognition to Action: VideoCutter with Confidence History & Debounce
- **Difficulty:** Intermediate
- **Type:** Engineering guide
- **Hook:** "Per-frame predictions are noise; segments are product."
- **Description:** `VideoCutter`: confidence history, dual LSTM+Chroma
  thresholds, debounce, transition filtering, region reconstruction → ffmpeg
  clip extraction (lossless `-ss`/`-to`). Teaches turning classifier output into
  usable artifacts.
- **Grounding:** `docs/packages/pole_ml/video-cutter-integration.md`, `docs/packages/pole_ml/PLAN.md` (Phase 5).
- **Sellable angle:** The "ML feature → shipped feature" bridge.

### B7 — CLI-First ML Pipeline: Eight Commands, One Workflow
- **Difficulty:** Intermediate
- **Type:** Workflow/engineering guide
- **Hook:** "Your model pipeline has a UI problem — the fix is eight typed commands."
- **Description:** `pole_tools` as the model workflow: process-data,
  train-model, process-embeddings, evaluate-video, find-by-similarity,
  audit-clips, samples-info, crop-trick. Why reproducible CLIs beat GUIs, and
  how the same services mount behind an API later.
- **Grounding:** `docs/packages/pole_tools/PLAN.md`, `docs/diagrams/pole_tools/FLOW.md`, `CLASSES.md`.
- **Sellable angle:** Rare "CLI-first MLOps" take; reproducible by readers.

### B8 — Testing an ML Pipeline Honestly
- **Difficulty:** Intermediate
- **Type:** Testing/quality guide
- **Hook:** "Model accuracy isn't the only test your pipeline needs."
- **Description:** The testing layer around the ML pipeline: fakeredis and
  mongomock substitute external stores, `.keras` loading gets stubbed,
  integration suites skip heavy training, and a ≥80% coverage gate keeps the
  suite honest. Keeping every stage—extract, train, index—testable.
- **Grounding:** `docs/packages/pole_ml/project/testing-plan.md`,
  `docs/app/pole_api/plan/PLAN_PHASE_20.md`.
- **Sellable angle:** Machine-learning-testing content is underserved; fits the
  "production ML" theme.

### B9 — Human-in-the-Loop Model Promotion
- **Difficulty:** Intermediate
- **Type:** ML-workflow/MLOps guide
- **Hook:** "The most important button in your ML pipeline is the one a human clicks."
- **Description:** The promotion flow: per-video `selected_for_training` flags
  as the manual quality gate, `readiness` stats, `train` (all windows) vs
  `retrain` (only unused windows) selection, then human `approve`/`activate`
  to make a run live. Why deploy is a decision, not an endpoint.
- **Grounding:** `docs/app/pole_api/slices.md` (PROMOTE semantics, training slice),
  `docs/app/pole_api/plan/PLAN_PHASE_25.md` (classify-first).
- **Sellable angle:** Human-in-the-loop ML-ops is a well-visited but rarely
  concrete topic; pairs with B4 (versioning).