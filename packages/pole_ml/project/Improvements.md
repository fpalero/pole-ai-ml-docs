# Improvements.md

Catalog of code-level fixes and broader improvements for `pole-train-model`. Entries follow the pattern:

```
Path • Finding • Severity (High / Medium / Low) • Suggested fix • Status
```

**All entries A1–A9 and B1–B6 are APPLIED** (status `✅`), each in a dedicated commit. No pending items remain.

| Point | Title | Status | Commit |
|-------|-------|--------|--------|
| A1 | Broken imports in `find_by_similarity` | ✅ Applied | `fc489ac` |
| A2 | `SkeletonRepository.predict` does not exist | ✅ Applied | `fc489ac` |
| A3 | Test/code drift for `_extract_window_features` | ✅ Applied | `132c57d` |
| A4 | Duplicate / stray imports | ✅ Applied | `8dde6c9` |
| A5 | MediaPipe timestamp monotonicity | ✅ Applied | `d0f3d63` |
| A6 | Zero-velocity feature placeholders | ✅ Applied | `feb6d6f` |
| A7 | Hardcoded MongoDB credentials | ✅ Applied | `01ad8df` |
| A8 | Datetime inconsistency / deprecation | ✅ Applied | `30f655b` |
| A9 | Docs drift from the `src` layout | ✅ Applied | `f8db308` |
| B1 | ChromaDB configuration inconsistency | ✅ Applied | `3b46cff` |
| B2 | Env / config normalization | ✅ Applied | `475f50f` |
| B3 | Repo hygiene — `.gitignore` for generated artifacts | ✅ Applied | `c5644f5` |
| B4 | Duplicated tool logic | ✅ Applied | `9154b0b` |
| B5 | Dependencies alignment | ✅ Applied | `628b130` |
| B6 | Test coverage (≥ 80 %) | ✅ Applied | `861533a` |

---

## A. Code-level fixes

### A1. Broken imports in `find_by_similarity`
- **Path:** `src/tools/find_by_similarity.py:14-21`
- **Finding:** Imports reference the old flat layout that no longer exists: `from ml import SkeletonEmbedding`, `from ml.skeleton_extractor import SkeletonExtractor`, `from ml.processing_pipeline import ProcessingPipeline`. These modules now live under `ml.processors/*`.
- **Severity:** High (tool cannot run).
- **Suggested fix:** Rewrite imports to `ml.processors.skeleton_extractor`, `ml.processors.processing_pipeline`, `ml.processors.skeleton_embedding`; drop `SkeletonStorage` usage since the pipeline builds windows before storage.
- **Status:** ✅ Applied in `fc489ac`.

### A2. `SkeletonRepository.predict` does not exist
- **Path:** `src/tools/find_by_similarity.py:140`
- **Finding:** Calls `skeletonChroma.predict(video_embedding)`, but `SkeletonRepository` (`src/ml/repositories/skeleton_repository.py`) exposes only `save/get_all/delete_sample/count/get_collection_info/verify_collection/close` — **no `predict`**.
- **Severity:** High (runtime `AttributeError`).
- **Suggested fix:** Use `ChromaClassifier` (`src/ml/classifiers/chroma_classifier.py`) for kNN prediction on the 128-d embedding, or add a `predict` to `SkeletonRepository`.
- **Status:** ✅ Applied in `fc489ac`.

### A3. Test/code drift for `_extract_window_features`
- **File:** `tests/test_video_cutter.py:36-44`
- **Finding:** Test asserts the `VideoCutter` has `_extract_window_features`, a method from the original design (`docs/crop-requirements.md`) that no longer exists in `src/tools/video_cutter.py`. The real flow extracts features inline in `_detect_target_class_windowed`.
- **Severity:** Medium
- **Suggested fix:** Update the test to assert the actual API (`_detect_target_class_windowed`, `_validate_segment_with_chroma`, `_extract_clips`) or restore the method as a thin wrapper.
- **Status:** ✅ Applied in `132c57d` (test now covers the real API; superseded by the full rewrite in `861533a`).

### A4. Duplicate / stray imports
- **Path:** `src/ml/repositories/window_repository.py:5-6`
- **Finding:** `from PIL import ExifTags` imported **twice** and unused; `PIL` is not a project dependency.
- **Severity:** Low.
- **Suggested fix:** Remove both lines.
- **Path:** `src/ml/processors/processing_pipeline.py:8`
- **Finding:** `from pyparsing import Optional` — wrong library, unused. Also unused `metrics` (line 11) and redundant `SkeletonEmbedding` import (line 14, re-imported inside `save_windows_embeddings`).
- **Severity:** Low.
- **Suggested fix:** Remove unused imports.
- **Status:** ✅ Applied in `8dde6c9`.

### A5. MediaPipe timestamp monotonicity
- **File:** `src/ml/processors/skeleton_extractor.py` (`RunningMode.VIDEO`), called from `src/ml/processors/processing_pipeline.py:67` (`process_video`) and `process_all_videos`.
- **Finding:** VIDEO mode requires **monotonically increasing** timestamps. `extract_skeleton_sequence` calls `self.reset()` at start, but that only helps the extractor itself; calling `extract_skeleton_from_frame` on the same instance across files/passes with non-monotonic timestamps causes the documented `Input timestamp must be monotonically increasing` failure (`CHANGES_SUMMARY.md`).
- **Severity:** High.
- **Suggested fix:** Always call `SkeletonExtractor.reset()` before each video; enforce timestamp construction from `frame_idx/fps` only; keep one extractor per video in `VideoCutter`.
- **Status:** ✅ Applied in `d0f3d63` (monotonicity check + `reset()` in `extract_skeleton_from_frame`).

### A6. Zero-velocity feature placeholders
- **File:** `src/ml/processors/skeleton_extractor.py:314-316`
- **Finding:** The last 4 of the 14 features are hardcoded `0.0`, so temporal motion is currently lost at training time.
- **Severity:** Medium (model ignores velocity, limiting temporal discrimination).
- **Suggested fix:** Compute real frame-to-frame velocity deltas (needs a previous frame passed in, or done in `processing_pipeline` across the window).
- **Status:** ✅ Applied in `feb6d6f` (real joint-angle velocity deltas via `_prev_velocity_features`).

### A7. Hardcoded MongoDB credentials
- **Files:** `src/tools/process_data.py`, `train_model.py:60`, `process_embeddings.py:61`, `evaluate_video.py:61`, `find_by_similarity.py:60`
- **Finding:** All tools hardcode `mongodb://admin:password@localhost:27017/?authSource=admin`. `pixi.toml` defines `MONGO_URI` for `evaluate-video` but the tools ignore it.
- **Severity:** High (security + config coupling).
- **Suggested fix:** Read `MONGODB_URI`/`MONGO_URI` env var (with dotenv) and use the CLI `--db-uri` consistently; never commit credentials in source.
- **Status:** ✅ Applied in `01ad8df` (`src/tools/config.py` with `get_mongo_uri`; no hardcoded credentials remain).

### A8. Datetime inconsistency / deprecation
- **File:** `src/ml/repositories/storage.py:102-103`
- **Finding:** `get_current_timestamp` uses `datetime.utcnow()` (deprecated) while the rest of the code uses `datetime.now(UTC)`.
- **Severity:** Low.
- **Suggested fix:** Replace with `datetime.now(UTC)`.
- **Status:** ✅ Applied in `30f655b`.

### A9. Docs drift from the `src` layout
- **Files:** `docs/DOCUMENTATION.md`, `README.md`, `CLAUDE.md`, `docs/PHASE1..4_PLAN.md`, `docs/video_cutter.md`
- **Finding:** Docs reference the old flat structure (`ml/skeleton_extractor.py`, `ml/storage.py`, `from tools.video_cutter import VideoCutter`, `from ml.processing_pipeline import ...`). Actual code is namespaced (`src/ml/processors/...`).
- **Severity:** Medium (guidance produces wrong import/ex supports).
- **Suggested fix:** Align docs with the real layout; keep `AGENTS.md` as the single-source structural reference.
- **Status:** ✅ Applied in `f8db308` (README + `docs/DOCUMENTATION.md` aligned to the `src/ml/*` namespace).

---

## B. Broader improvements

### B1. ChromaDB configuration inconsistency
- **Finding:** Components disagree on persist dir and collection name:
  - `SkeletonRepository` default persist `./FeaturesEmbeddings`, collection `skeleton_vectors`.
  - `processing_pipeline.save_windows_embeddings` uses collection `movement_embeddings`.
  - `HybridClassifier` default persist `./chroma_db`, collection `movement_embeddings`.
  - `ChromaClassifier` default persist `./chroma_data`, collection `skeleton_vectors`.
  - `scripts/crop-clips.sh` default Chroma path `FeaturesEmbeddings_2_classes/`.
- **Severity:** High (data written to one collection is invisible to classifiers pointing elsewhere).
- **Suggested fix:** Define a single config (persist dir + collection name) used by all repositories/classifiers/tools.
- **Status:** ✅ Applied in `3b46cff` (canonical: persist `./FeaturesEmbeddings`, collection `movement_embeddings` everywhere).

### B2. Env / config normalization
- **Finding:** Mongo URI, model paths, and Chroma paths are scattered and partly hardcoded; `pixi.toml` env vars are inconsistently honored.
- **Severity:** Medium.
- **Suggested fix:** One `.env` + small config loader; threads `--db-uri`, `--model`, `--chroma-path` consistently across tools.
- **Status:** ✅ Applied in `475f50f` (config getters + `.env` loader in `src/tools/config.py`).

### B3. Repo hygiene — no `.gitignore` for generated artifacts
- **Finding:** `models/lstm_model_normal_epoch*.keras` (50 × ~2.8 MB ≈ 140 MB), `output_clips/`, `checkpoint.json`, `chroma*.sqlite3`, `FeaturesEmbeddings/` are tracked/generated without ignore rules.
- **Severity:** Medium (repo bloat, accidental commits).
- **Suggested fix:** Add `.gitignore` for `models/*_epoch*.keras`, `output_clips/`, `checkpoint.json`, `*.sqlite3`, `FeaturesEmbeddings/`, `chroma_data/`, `results/`, `output/`.
- **Status:** ✅ Applied in `c5644f5` (`.gitignore` extended; generated artifacts untracked).

### B4. Duplicated tool logic
- **Location:** `src/tools/evaluate_video.py` and `src/tools/find_by_similarity.py` share ~80% of the extraction/prediction flow; `train_model.py` duplicates `save_results`/serialization logic also present in `processing_pipeline`.
- **Severity:** Medium.
- **Suggested fix:** Extract shared helpers (video → windows → predict → save JSON/CSV) into a shared module under `src/tools` and reuse.
- **Status:** ✅ Applied in `9154b0b` (`src/tools/eval_utils.py`; `evaluate_video` + `find_by_similarity` refactored to use it).

### B5. Dependencies alignment
- **File:** `requirements.txt` lists `torch`, `torchvision`, `ffmpeg-python`, `flask`-era tools not used by `src/`; pixi uses `tensorflow-cpu` only and `ffmpeg` is invoked via `subprocess`.
- **Severity:** Low.
- **Suggested fix:** Trim unused deps; document that ffmpeg is a system binary, not a Python package; align `requirements.txt` (`>=3.9`) with pixi (python `3.12`).
- **Status:** ✅ Applied in `628b130`.

### B6. Test coverage (target ≥ 80 %)
- **Reference:** `docs/project/testing-plan.md`.
- **Current state:** `tests/` holds one loose `test_video_cutter.py`; `test/` holds old non-pytest exploratory scripts.
- **Severity:** Medium.
- **Suggested fix:** Consolidate under `tests/` with pytest + mocks (MediaPipe, OpenCV, Mongo, ChromaDB). Add `conftest.py` fixtures; cover `src/ml` and `src/tools`; wire coverage via `pytest --cov=src --cov-report term-missing`.
- **Status:** ✅ Applied in `861533a` — **478 tests pass, 89.31 % coverage** across `src/ml` + `src/tools` (above the ≥ 80 % target). Legacy `test/` scripts removed; pytest + pytest-cov added to pixi deps.

---

## Suggested prioritization

> Historical — all items below have been completed in commits A1–B6 (see status table above).

1. (High) **A1, A2, A5** — unblock tools (`find_by_similarity`, video cutter extraction).
2. (High) **A7** — remove hardcoded credentials.
3. (Medium) **A3, A9, B1, B3, B6** — test accuracy, docs alignment, ChromaDB consistency, repo hygiene, coverage.
4. (Low) **A4, A6, A8, B2, B4, B5** — cleanup, real velocity features, datetime, config, deduplication, deps.