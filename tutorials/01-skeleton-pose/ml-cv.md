# Theme 01 — Skeleton & Pose · Audience: ML / CV Engineers

> Deep technical tutorials for engineers who already know MediaPipe/TensorFlow
> and want the *battle-tested* details: normalization that actually works,
> biomechanical feature design, and honest small-data practices.

## Catalog

### A1 — Production-Grade Pose Extraction with MediaPipe
- **Difficulty:** Intermediate
- **Type:** Technical deep-dive
- **Hook:** "Copy-paste MediaPipe gives you landmarks; it does NOT give you a classifier-ready dataset."
- **Description:** Walk through the real `SkeletonExtractor`: frame-by-frame
  Pose Landmarker in `RunningMode.VIDEO`, raw landmark capture, and the two
  normalizations that make vectors translation- and scale-invariant
  (hip-center shift + shoulder-width scale) plus visibility filtering
  (threshold ≥ 0.7). Reader leaves able to replicate the pattern on any pose task.
- **Grounding:** `docs/diagrams/pole_ml/CLASSES.md`; source
  `packages/pole-train-model/src/pole_ml/processors/skeleton_extractor.py`.
- **Sellable angle:** Evergreen foundational article; LTV as the anchor of a
  "pose → embedding → classifier" series.

### A3 — From Video to Vectors: Biomechanical Feature Engineering
- **Difficulty:** Advanced
- **Type:** Technical deep-dive
- **Hook:** "Sometimes hand-crafted joint angles beat an end-to-end black box — here's the evidence pipeline."
- **Description:** `BiomechanicalProcessor` converting normalized landmark
  time-series into per-frame joint angles/speeds; how these feed 30×14 sliding
  windows and 8-signal histogram metrics (resampled to 100 pts/phase). Includes
  the data-flow contract: extract → transform → persist.
- **Grounding:** `docs/diagrams/pole_ml/FLOW.md`, `docs/diagrams/pole_ml/CLASSES.md`.
- **Sellable angle:** Taps the "small data vs big models" debate; positions as
  the domain-expertise article.

### A4 — Sliding Windows, Data Augmentation & Small Datasets
- **Difficulty:** Intermediate
- **Type:** Practical guide
- **Hook:** "You don't need 10k videos — you need the right 200 and the right augmentations."
- **Description:** The full small-data playbook as implemented: sliding windows
  (stride 5, 30-frame), mirror/timing/perturbation augmentation, class weights,
  and Chroma-based oversampling as a few-shot assist for new classes.
- **Grounding:** `docs/packages/pole_ml/project/retraining-tool-plan.md`
  (Pipeline D), `docs/packages/pole_ml/PLAN.md` (Phases 1–3).
- **Sellable angle:** The #1 pain of CV engineers; strong practical ROI.

### A2 — The "Monotonically Increasing Timestamp" Bug
- **Difficulty:** Beginner → Intermediate (anyone)
- **Type:** Debugging case study
- **Hook:** "MediaPipe crashed with `Input timestamp must be monotonically increasing` — here's why and the 3-line fix."
- **Description:** A real production bug story: VIDEO mode requires monotonic
  timestamps; reuse of one extractor instance across files/passes breaks it.
  Teaches `reset()` lifecycle discipline and per-video extractor instances.
- **Grounding:** `docs/packages/pole_ml/project/Improvements.md` (finding A5,
  fix in `d0f3d63`).
- **Sellable angle:** High-traffic SEO debugging article; great funnel piece.

### A5 — Automatic Phase Detection in Sports Video
- **Difficulty:** Advanced
- **Type:** Algorithms/analysis guide
- **Hook:** "Coach, the 90% took off at second 1.4 — no manual frame marking required."
- **Description:** Segment a trick into entrance/execution/exit automatically:
  reference data and metric time-series (handspring feature) drive
  phase detection without hand-labeled frames. Covers phase drift failure
  modes and how phases feed per-phase coaching analysis.
- **Grounding:** `docs/app/pola_agent/phase-6-reference-data-hardened-analysis/PAIML-POLE-AGENT-010/011.md`,
  `docs/app/pola_agent/agent_requirements.md`.
- **Sellable angle:** Rare "automated phase/event detection" content in sport
  analysis; pairs with A3 for a biomechanics series.

### A6 — 8-Signal Histogram Analysis & Cohort Z-Scores
- **Difficulty:** Advanced
- **Type:** Analytics/feature-engineering guide
- **Hook:** "Judge a performance by shape, not by frame — and against a cohort, not in a vacuum."
- **Description:** The two-pass analysis behind coaching: (1) resample each
  trick to 300 points (100 per phase) per metric and aggregate cohort
  mean/std; (2) score every athlete against it with z-scores (0-100) and
  auto-extract critical-frame JPEGs at |z|>1. Error isolation means one bad
  video never sinks the job.
- **Grounding:** `docs/app/pole_api/slices.md` (slice tools), `docs/app/pole_api/phase-11-histogram-analysis/PAIML-POLA-API-010..020.md`.
- **Sellable angle:** Original "cohort-normalized shape analysis" framing;
  strong overlap with A3/A5 for a full biomechanics series.