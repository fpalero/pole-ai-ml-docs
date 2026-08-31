# Implementation Plan — `pole-train-model` (`pole_ml` + `pole_tools` CLI)

> **Status:** Core pipeline complete (skeleton extraction, biomechanical features, sliding windows,
> LSTM training, embeddings, Chroma, hybrid classifier, video cutter). Two-phase extraction split
> (`LandmarkExtractor` / `BiomechanicalDataProcessor` / `HistogramDataProcessor`) complete. ~549
> tests at 81.63% coverage. Future work: automatic phase detection, threshold discovery, batch
> extraction polish, reference metrics.
> **Source docs:** `docs/packages/pole_ml/` (PHASE1–4 plans, PROJECT_STATUS, DOCUMENTATION,
> IMPLEMENTATION_SUMMARY, TODO, crop/video-cutter docs, `project/` spec + testing-plan).

---

## 1. Feature Context & Objective

- **Goal:** Turn raw trick videos into (a) classification (LSTM + ChromaDB hybrid), (b) 128-dim
  embeddings for similarity search, and (c) automatic clip extraction. Two explicit phases: Phase 1
  `LandmarkExtractor` writes `videos.landmarks` to the app DB; Phase 2 processors
  (`BiomechanicalDataProcessor` → `skeleton_windows`, `HistogramDataProcessor` →
  `skeleton_histograms`) read from the DB.
- **Non-Functional Constraints:** normalization = hip-center translation + shoulder-width scale
  invariance; visibility filter ≥ 0.7; extraction stride default 5; 30-frame windows (stride param);
  ≥ 80% coverage; two DBs (`pola_api` app data, `skeleton_data` ML data).
- **Affected Components:**
  - `pole_ml/processors/` — `skeleton_extractor`, `data_extractor` (LandmarkExtractor),
    `data_processor`, `biomechanical_processor`, `histogram_processor`, `processing_pipeline`,
    `skeleton_embedding`, `data_augmentation`, `blip_caption`.
  - `pole_ml/models/` — `model_trainer`, `model_persistence`, `model_evaluator`, `model_data`,
    `video_training`.
  - `pole_ml/classifiers/` — `lstm_classifier`, `chroma_classifier`, `hybrid_classifier`, `base`.
  - `pole_ml/repositories/` — `storage` (Mongo), `window_repository`, `video_repository`,
    `skeleton_repository` (ChromaDB).
  - `pole_ml/filters/` — `transition_filter`, `clip_utils`.
  - `pole_tools/cli/` — `process_data`, `extract_data`, `train_model`, `process_embeddings`,
    `samples_info`, `evaluate_video`, `find_by_similarity`, `video_cutter`, `audit_clips`,
    `migrate_windows`, `clip_resolver`, `eval_utils`.
- **Assumptions:** Mongo + ChromaDB available via env; MediaPipe model at `models/`; tools run via
  `pixi run <task>` (cwd set per task).

---

## 2. Architectural Layering (The "Where")

- **Domain:** landmarks (33×4), biomechanical features (14/frame), skeleton windows (30×14),
  histograms (8 metrics, resampled 300), embeddings (128-d), class labels
  (`handspring`, `shouldermount`, `transition`).
- **Application:** `DataExtractor`/`DataProcessor` interfaces; `ProcessingPipeline`; `ModelTrainer`
  (LSTM full + fine-tune, LOO); `SkeletonEmbedding`; `VideoCutter`; `EvaluationMetrics`.
- **Infrastructure:** `SkeletonStorage`/`WindowRepository`/`VideoRepository` (Mongo `skeleton_data`
  + app `videos`), `SkeletonRepository` (ChromaDB cosine), MediaPipe Pose Landmarker, TensorFlow
  Keras persistence (`.keras`, `*_encoder.pkl`, metadata JSON).
- **Presentation:** CLI entry points (`python -m pole_tools.cli.*`) and pixi tasks.

---

## 3. Implementation Roadmap (Atomic Steps)

### Phase 1: Skeleton extraction — ✅ DONE
- [x] `SkeletonExtractor` — MediaPipe Pose (VIDEO mode, monotonic timestamps), 33 landmarks,
  normalization (hip-center + shoulder-width), visibility filter ≥ 0.7, 14 biomechanical
  features/frame.
- [x] Sliding window builder (W=30, stride=5), zero-pad short videos.

### Phase 2: Training data prep — ✅ DONE
- [x] Directory-structured video corpus per class; error handling for corrupt/short videos.
- [x] Mongo persistence (`skeleton_data`) with progress tracking.

### Phase 3: Model training — ✅ DONE
- [x] Three-layer LSTM (feature_vector 128-d), 85/15 + Leave-One-Out splits, mixed precision,
  gradient clipping, tf.data pipeline, data augmentation, class weighting.
- [x] Evaluation: confusion matrix, F1, ROC-AUC; per-epoch `.keras` checkpoints + history/metadata.

### Phase 4: Embeddings + classifiers — ✅ DONE
- [x] `SkeletonEmbedding` (128-d bottleneck) → ChromaDB (`SkeletonRepository`, cosine).
- [x] `ChromaClassifier` (k-NN voting, confidence), `LSTMClassifier` (proba + confidence),
  `HybridClassifier` (LSTM-first, Chroma fallback).

### Phase 5: Video cutter — ✅ DONE
- [x] `VideoCutter` — confidence history, debounce, dual LSTM+Chroma thresholds, transition
  filtering, region reconstruction → ffmpeg clip extraction; YAML config in `config/`.

### Phase 6: Two-phase extraction split — ✅ DONE (commits `cc0af52`..`e02fb26`)
- [x] `LandmarkExtractor` (Phase 1) — frame dicts `{frame, timestamp, landmarks[33][4],
  visibility_count}` → `videos.landmarks` + `extracted=true` (app DB only).
- [x] `BiomechanicalDataProcessor` (Phase 2) — 14 features → 30-frame windows →
  `skeleton_data.skeleton_windows`.
- [x] `HistogramDataProcessor` (Phase 2) — 8 metrics M-01..M-08 → resampled 300 (100/phase) →
  `skeleton_data.skeleton_histograms` (idempotent delete+re-insert, requires `phase_frames`).
- [x] CLI split: `extract-data` (extraction only) + `process-data` (processing only, validates
  `extracted=true`).
- [x] CLI integration tests against `_testing` DBs (`a830cf1`).

### Phase 7: Future — Analysis & reference data
> **PO decision 2026-08-13:** automatic phase detection is **no longer a requirement** — phases are
> entered **manually** via `PUT /api/training/clips/{id}/phase-frames`. The `PhaseDetector` and its
> `histogram_analyzer` fallback are removed via `PAIML-POLE-AGENT-015`.
- [x] ~~Application automatic phase detection (PD-01..05 thresholds)~~ **REMOVED (PO)** — phases manual only.
- [x] ~~Application LLM threshold discovery for phase config~~ **REMOVED** — superseded by fixed `|z|>1` thresholds.
- [ ] Application batch extraction perf (multi-GPU / parallel workers).
- [x] Application reference data bootstrap — the Mongo `signal_histograms` cohort is produced
      automatically by the histogram-analysis job; no manual reference builder is needed (the Postgres
      `pole_tools.reference_builder` was removed).

---

## 4. Quality Gates & Testing Commands (DoD)

- **Unit Tests:** `pixi run test` (pytest in `packages/pole-train-model` with `--cov`) — ≥ 80%.
- **Integration Tests:** `pixi run test-api` (API on `_testing` DBs, UC-82..90); CLI integration
  (`test_cli_integration.py`, UC-82..90 matrix: extract→process happy path, process-without-extract
  error, idempotent re-run, `--phase-frames` skip path); `pixi run test-chatbot-live` (WS→jobs→ffmpeg);
  `pixi run fe-e2e` (FE+BE Playwright). Aggregated by `pixi run test-integration` with a `_testing`-suffix guard.
- **Automation:** CI enforces coverage via `[tool.coverage.report] fail_under = 80`.
- **Database Target:** `pole_api_testing` (app videos) + `skeleton_data_testing` (windows +
  histograms); Chroma temp dir per session.
- **Coverage Requirement:** ≥ 80% (currently 81.63% / ~549 tests).
- **Additional Checks:** data shape scripts (`check-data-shape`, `data-analysis`),
  `audit-clips`, `migrate-windows`.

---

## 5. Defined Use Cases (Gherkin + Technical Matrix)

### UC-ML-01: Extract landmarks from a clip (CLI)
- **Given** a clip registered in `pole_api_testing.videos` with a local video file
- **When** user runs `pixi run extract-data`
- **Then** command exits 0
- **And** database `videos` doc has `extracted=true` and non-empty `landmarks` (frame/timestamp/33×4 + visibility_count)

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | CLI `python -m analysis_tools.extract_data` |
| Request Method | CLI (env `POLA_API_DB`, `SKELETON_DB`, `MONGODB_URI`) |
| Required Headers | n/a |
| Payload Example | `--video-ids <id>` (optional) |
| DB State (Before) | clip `extracted=false` |
| DB State (After) | `extracted=true`, landmarks written to app DB only |

### UC-ML-02: Process biomechanical windows
- **Given** an extracted clip
- **When** user runs `pixi run process-data`
- **Then** command exits 0
- **And** database `skeleton_data_testing.skeleton_windows` has windows with label = class

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | CLI `python -m pole_tools.cli.process_data` |
| Request Method | CLI |
| Required Headers | n/a |
| Payload Example | `--video-ids <id>` (optional) |
| DB State (Before) | extracted clip, no windows |
| DB State (After) | windows created (30×14); re-run idempotent |

### UC-ML-03: Process histogram metrics
- **Given** an extracted clip with `phase_frames` set
- **When** user runs `pixi run process-data`
- **Then** command exits 0
- **And** database `skeleton_data_testing.skeleton_histograms` has one doc: 8 metrics, `resampled` 300, `phase_frames` copied

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | CLI `python -m pole_tools.cli.process_data` |
| Request Method | CLI |
| Required Headers | n/a |
| Payload Example | `--phase-frames` variants |
| DB State (Before) | extracted + phase_frames, no histogram |
| DB State (After) | 1 histogram doc (delete+re-insert); missing phase_frames → skip |

### UC-ML-04: Process without extraction fails
- **Given** a video that was never extracted
- **When** user runs `pixi run process-data`
- **Then** command exits non-zero with a clear error
- **And** database has no windows/histograms for that video

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | CLI `python -m pole_tools.cli.process_data` |
| Request Method | CLI |
| Required Headers | n/a |
| Payload Example | n/a |
| DB State (Before) | video `extracted=false` |
| DB State (After) | no windows/histograms; error reported |

### UC-ML-05: Train a full LSTM model
- **Given** windows with `selected_for_training=true` for the target classes
- **When** user runs `pixi run train-model --classes handspring,shouldermount --mode full`
- **Then** command exits 0
- **And** filesystem `models/runs/<run_id>/` contains `.keras`, `*_encoder.pkl`, `metadata.json`

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | CLI `python -m pole_tools.cli.train_model` |
| Request Method | CLI |
| Required Headers | n/a |
| Payload Example | `--loo`, `--mode full\|fine-tune`, `--classes` |
| DB State (Before) | windows available |
| DB State (After) | run artifacts written; windows annotated with `training_runs` |

### UC-ML-06: Embed windows and retrieve by similarity
- **Given** trained model + windows
- **When** user runs `pixi run process-embeddings` then `pixi run find-by-similarity`
- **Then** both commands exit 0
- **And** ChromaDB has 128-d vectors; similarity search returns ranked matches with scores

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | CLI `python -m pole_tools.cli.process_embeddings` / `find_by_similarity` |
| Request Method | CLI |
| Required Headers | n/a |
| Payload Example | `--model`, `--chroma-collection` |
| DB State (Before) | windows in `skeleton_data` |
| DB State (After) | embeddings in Chroma (per model, idempotent) |

### UC-ML-07: Crop clips via video cutter
- **Given** a source video + cutter YAML config
- **When** user runs `pixi run crop-trick`
- **Then** command exits 0
- **And** output clips exist in `output_clips/` with detected boundaries

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | CLI `python -m pole_tools.cli.video_cutter` |
| Request Method | CLI |
| Required Headers | n/a |
| Payload Example | `--config config/cutter-<trick>.yaml`, `chroma_only` mode |
| DB State (Before) | source + config |
| DB State (After) | clips written; invalid source → error, no crash |

---

## 6. Risks and Mitigations

- **Risk:** MediaPipe VIDEO mode requires monotonic timestamps — restarts per source. **Mitigation:** documented + reset per source.
- **Risk:** histogram requires `phase_frames`; auto-detection not available. **Mitigation:** manual phase-frames endpoint + clear skip reasons; PD analysis tracked.
- **Risk:** test contamination of prod DBs. **Mitigation:** `_testing` DB guard in conftest; CLI tests pass env overrides.
- **Risk:** two distributions sharing the `pole_tools` namespace. **Mitigation:** config lives in pole-train-model, facade re-exports the surface; import discipline documented.
- **Risk:** coverage target slipping below 80% as new processors land. **Mitigation:** `fail_under = 80` enforced; per-module matrix in testing-plan.md.

---

## 7. Open Questions and Decisions

- Decision: two DBs — app `videos` (landmarks, phase_frames) vs `skeleton_data` (windows, histograms).
- Decision: `process` runs both processors in a loop; idempotent (delete+re-insert).
- Decision: extraction applies to clips only (`kind == "clip"`); `transition` is a noise/negative class in the cutter.
- Open: automatic phase detection (PD-01..05) schedule and validation data.
- Open: reference metrics bootstrap (who seeds `reference_metrics` for the agent).
