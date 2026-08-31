# Re-training Tool Plan: Adding New Tricks & Classes

**Status:** Plan approved (Phase 1 complete). Implementation not started.
**Date:** 2026-08-03 (revised — no `add-trick`; reuses `process_data.py` + `process_embeddings.py` with MongoDB tracking fields)
**Target deliverable:**

1. Reuse the existing tools to ingest a new trick: `process_data.py` (windows → MongoDB) and `process_embeddings.py` (128-d embeddings → ChromaDB).
2. Add **tracking fields to the MongoDB window documents** so we know which windows were already embedded and which were used in training / re-training.
3. `pixi run samples-info` — report per-class/per-video sample status so the backend API can show it and **the user decides when to promote** a class to the LSTM.
4. `pixi run train-model` (modified) — retrain the LSTM on a user-selected set of classes (`full` or `fine-tune`) and record the run.

---

## 1. Goal

Let an operator teach the Pole AI model a **new trick** (new class):

1. Drop the already-cut clips of the new trick in a folder (e.g. `videos/backflip/`). Cutting/review happens **outside** this repo (backend API runs `pole-crawler` + `VideoCutter` + human review).
2. `process_data.py` extracts windows → MongoDB with the folder name as the label.
3. `process_embeddings.py` embeds the **pending** windows → ChromaDB. A Mongo field prevents re-embedding the same windows.
4. `samples-info` shows sample counts/status per class so the user (via the backend API) decides when there are enough samples.
5. `train-model` retrains the LSTM on the old classes + the new one (full or fine-tune) and marks the windows used.
6. Until promoted, the new class is classified via the **ChromaDB nearest-vector path** (`HybridClassifier` already falls back to kNN).

---

## 2. Current architecture recap (what we build on)

```
videos/<class>/*.mp4
  → process_data.py → SkeletonExtractor (MediaPipe, 14 features/frame)
  → ProcessingPipeline (sliding windows 30×14, stride 5) → MongoDB (label = folder name)
  → process_embeddings.py → SkeletonEmbedding → 128-d → ChromaDB (movement_embeddings, ./FeaturesEmbeddings, cosine)
  → ModelData.get_training_data → ModelTrainer.train (LSTM, 128-d feature_vector) → models/*.keras + encoder.pkl
  → HybridClassifier (LSTM first, ChromaDB kNN fallback when LSTM confidence < 0.7)
  → VideoCutter (windowed detection, dual thresholds, debounce) → ffmpeg clips
```

- Classes today: `handspring`, `shouldermount`, `transition`. `transition` is also the noise/negative class in the cutter.
- Label comes from the **parent folder name** (`process_all_videos`).
- ChromaDB collection `movement_embeddings` (persist `./FeaturesEmbeddings`) holds 128-d vectors with `label` metadata (~1482 currently).
- `process_embeddings.py` currently loads **all** windows and re-embeds every run — there is no "already embedded" check, so repeated runs can duplicate Chroma entries. This is what the new tracking fields fix.

---

## 3. Design decisions

| Decision | Choice |
|----------|--------|
| New-class ingestion | **Reuse `process_data.py` + `process_embeddings.py`** — no `add-trick` tool. |
| Input videos | **Already-cut clips** in a folder per class. Raw→cut is owned by the backend API. |
| Embedding dedup / provenance | **Tracking fields on the Mongo window document** (`embedding_models` list, `training_status`, `last_training_run`, …). |
| Promotion | **User-driven** — `samples-info` provides the numbers; the user (backend API) decides when to promote. |
| Retrain tool | **`train-model` (modified)** — explicit class list, `--mode full\|fine-tune`, augmentation, class-weight, records `training_runs`. |
| Old data source | **Reuse existing Mongo windows** for old classes; only the new trick is freshly processed. |
| Class-weight / augmentation | Expose flags; balanced class weights already built into `ModelTrainer`; `SkeletonAugmenter` exists but is not exposed by tools yet. |

---

## 3.1 Alternative pipelines considered (solutions for re-training)

These were evaluated before agreeing the design above. Documented for reference; viable depending on data volume and how close the new trick is to existing classes.

### Pipeline A — Full retrain from scratch
`extract → windows (old Mongo + new) → ModelTrainer rebuilds net with n+1 classes → new encoder + re-embed all classes`.
- **Pros:** simplest, most robust, no stale-architecture risk; well supported by `ModelTrainer.train`.
- **Cons:** needs the old data preserved (it is, in Mongo); discards learned 128-d space (requires re-embedding); slowest.
- **Verdict:** default mode (`--mode full`).

### Pipeline B — Fine-tune to add a class (transfer learning)
Load existing `.keras`, keep layers up to `feature_vector`, swap the softmax head to `n+1`, retrain on combined data (optionally freeze the encoder).
- **Pros:** faster; keeps the 128-d feature space stable so existing Chroma vectors stay valid; good when the new trick is similar to existing ones.
- **Cons:** needs a new `ModelTrainer.fine_tune` method; risk of catastrophic forgetting if the head is trained too aggressively; class order must match the existing encoder.
- **Verdict:** chosen as the second mode (`--mode fine-tune`).

### Pipeline C — ChromaDB / nearest-vector only (few-shot, no retrain)
Add `<trick>` embeddings to `movement_embeddings`; classify by kNN (`ChromaClassifier.predict_weighted`). The existing `HybridClassifier` already falls back to ChromaDB when LSTM confidence is low, so a new label can be returned without any model change.
- **Pros:** zero retraining; works with a handful of clips; the exact "use directly Chroma DB to find the closest vector" idea.
- **Cons:** kNN quality depends on embedding quality and label density; no temporal LSTM smoothing for the new class; confident old-class predictions won't fall back.
- **Verdict:** the few-shot path for a class that has not been promoted yet. This is the default state right after `process_embeddings`.

### Pipeline D — Few-shot assist at data level
Compensate for a tiny new class without changing the model: balanced class weights (already in `ModelTrainer`), `SkeletonAugmenter` synthetic copies, and/or Chroma-based oversampling of the new class windows.
- **Pros:** cheap, local change; preserves the existing model.
- **Cons:** augmentation on 14-d biomechanical features is limited; cannot fully replace real data.
- **Verdict:** exposed as `--augment` / `--class-weight` flags on `train-model`, combined with C until promotion.

### Pipeline E — Classifier ensemble / threshold steering
Instead of swapping the model, adjust the hybrid thresholds (`lstm_threshold`, `chroma_k`, `chroma_confidence_threshold`) so a new trick triggers Chroma fallback more often.
- **Pros:** zero model change.
- **Cons:** global threshold changes affect old classes too; brittle.
- **Verdict:** not implemented; documented for tuning only.

### Combined recommendation (adopted)
**C by default** after ingestion (embed + kNN, no LSTM change) → the user reviews `samples-info` and decides to promote → `train-model` runs **A or B** (configurable) with **D** (weights + optional augmentation) during retrain.

---

## 4. Ingestion flow (reuses existing tools)

```
new clips → videos/<trick>/
  → pixi run process-data --video-dir videos/<trick>
      ProcessingPipeline.process_data → windows → MongoDB (label=<trick>,
      embedding_models=[], training_status=untrained)
  → pixi run process-embeddings --model ./models/lstm_model_normal.keras
      save_windows_embeddings(windows not yet embedded by this model) → ChromaDB (label=<trick>)
      → appends the model to each window's embedding_models (+ embedded_at)
```

- `process_data.py` already labels windows by the parent folder name.
- A window now tracks **every model** that embedded it in `embedding_models` (a list), so a
  window can be embedded by several models over time. There is no single `embedding_status`/
  `embedding_model`: stale = the current model is **not** in `embedding_models`.
- **No new ingestion tool.** `add-trick` is dropped.

---

## 5. MongoDB tracking fields

### 5.1 Window document fields (in `skeleton_windows`)

```python
# set at creation in storage.save_skeleton_data
'embedding_models': [],      # every model that embedded this window (dedup)
'embedded_at': None,
'training_status': 'untrained',    # untrained | trained
'last_training_run': None,         # run_id of the most recent run that used this window
'last_trained_at': None,
```

Semantics:
- **`embedding_models`** — a window is embeddable (pending/stale) when the current model is
  **not** in `embedding_models`. Embeddings are **model-specific**: after a retrain the
  `feature_vector` changes, so old vectors are stale. `process-embeddings --force` re-embeds
  everything regardless (it appends the model again — no duplicates).
- **`training_status`/`last_training_run`** — "used in the latest run", not absolute (full retrains legitimately reuse all windows). Full provenance lives in `training_runs`.

### 5.2 `training_runs` collection (one doc per retrain)

```python
{ 'run_id': ..., 'timestamp': ..., 'mode': 'full|fine-tune',
  'classes': [...], 'window_ids': [...], 'model_path': ...,
  'metrics': {...} }
```

### 5.3 Backfill / migration for existing windows
- Add the new fields with defaults (`embedding_models=[]`, `training_status='untrained'`) to all existing docs, and migrate a legacy `embedding_model: "<str>"` into `embedding_models: ["<str>"]`.
- After backfill, run `process-embeddings --force` once to reconcile ChromaDB with the new model, or leave existing windows for the next incremental run.

---

## 6. Tool 1 — `samples-info` (MongoDB sample reporting)

### Purpose
Read the window documents from MongoDB and summarize them so the **backend API** can show the user, per class, how many samples exist and their processing status — and the user can **decide when to promote** a class to the LSTM.

### Output
JSON (default) or CSV, aggregate + detail:

```
{
  "generated_at": "...",
  "total_windows": 0,
  "total_videos": 0,
  "classes": [
    {
      "label": "handspring",
      "windows": 0,
      "videos": 0,
      "per_video": [ {"video_id": "...", "windows": 0}, ... ],
      "embedded": 0, "pending_embedding": 0,
      "trained": 0, "untrained": 0,
      "avg_visibility": 0.0,
      "has_features": true
    }, ...
  ]
}
```

### Reused components
`WindowRepository.get_all_batches` / `get_all` (Mongo windows with `label`, `video_id`, `features`, `visibility_count`, and the new status fields), `tools.config.get_mongo_uri`.

### CLI surface

```
pixi run samples-info \
    [--label <name>]           # filter to one class (optional)
    [--output-format json|csv] # default json
    [--output path]            # write to file instead of stdout
    [--db-uri ...]             # override Mongo (default get_mongo_uri())
```

New pixi task `samples-info` mirroring the existing task style (`PYTHONPATH=./src`).

---

## 7. Tool 2 — `train-model` (modified) — retrain / promote

### What changes
The current `src/tools/train_model.py` retrains on **all** windows in Mongo. To support promotion of a new class it must accept:

- `--classes <label1> <label2> ...` — restrict training to the given class labels (e.g. `handspring shouldermount transition backflip`). Default: all classes present.
- `--mode normal|loo|fine-tune` — `normal` (85/15 split, today's default), `loo` (Leave-One-Video-Out, existing flag), `fine-tune` (new).
- `--augment N` — apply `SkeletonAugmenter` N synthetic copies per sample (already implemented in `ProcessingPipeline.train_model_normal` / `train_model_loo`, currently not exposed by the CLI).
- `--no-class-weight` — disable the balanced class weights already applied by `ModelTrainer`.
- `--reembed|--no-reembed` — re-embed the selected classes after retrain (default on).
- Existing `--db-uri`, `--output-dir`, `--loo`.

### Retrain regimes (per class selection)
- `--mode normal` (full): `ProcessingPipeline.train_model_normal(documents_filtered, ...)` → `ModelTrainer.train` rebuilds the net with `n+1` classes.
- `--mode fine-tune`: **new method** `ModelTrainer.fine_tune(...)` — load existing `.keras`, keep layers up to `feature_vector`, replace the final `Dense(num_classes)` with `Dense(n+1)`, recompile, retrain on the selected classes (optionally frozen encoder). The 128-d space stays stable.
- `--mode loo`: existing Leave-One-Out evaluation on the selected classes.

### After training
- Save model (`models/*.keras`), label encoder (`*_encoder.pkl`, now includes the new class), history + metadata JSON (existing behavior).
- Insert a `training_runs` document with the window ids used.
- Mark those windows `training_status='trained'`, `last_training_run=<run_id>`, `last_trained_at=now`.
- **Re-embed all selected classes** (`--reembed`) so the ChromaDB feature space matches the new model: `mark_trained` now **appends** the model to each window's `embedding_models` per §5.1 rule.

### CLI surface

```
pixi run train-model \
    --classes <label1> [<label2> ...]   # retrain on these classes (default: all)
    --mode normal|loo|fine-tune         # default normal
    --augment N                         # SkeletonAugmenter copies (default 0)
    --no-class-weight                   # disable balanced class weights
    --reembed|--no-reembed              # re-embed all selected classes after retrain
    --db-uri ...                        # override Mongo (default get_mongo_uri())
    --output-dir ./models
```

---

## 8. New / modified source files

| File | Change |
|------|--------|
| `src/ml/repositories/storage.py` | **Extend** — set `embedding_models`/`training_status` defaults when saving windows. |
| `src/tools/process_embeddings.py` / `save_windows_embeddings` | **Modify** — embed only windows not yet embedded by the model (`--force` to re-embed all); append model to `embedding_models` (+ `embedded_at`) after Chroma save. |
| `src/tools/samples_info.py` | **New** — aggregate Mongo windows into per-class/per-video status stats (JSON/CSV). |
| `src/tools/train_model.py` | **Modified** — `--classes`, `--mode` (add `fine-tune`), `--augment`, `--no-class-weight`, `--reembed`; filter Mongo documents by the class list; write `training_runs` + mark windows trained. |
| `src/ml/models/model_trainer.py` | **Extend** — add `fine_tune(...)` (load existing, swap head, retrain). |
| `src/ml/repositories/window_repository.py` | **Extend** — list-based status filters (`get_pending_embeddings`, `get_by_label`), `mark_embedded`, `mark_trained`, backfill migration. |
| `pixi.toml` | add `samples-info` task; extend `train-model` task args. |
| `tests/test_samples_info.py`, `tests/test_train_model.py` (classes/fine-tune), `tests/test_model_trainer.py` (fine_tune), `tests/test_process_embeddings.py` (status skip), `tests/test_storage.py` (defaults), `tests/test_window_repository.py` (status queries) | **New/extended** tests. |

### Reused assets (no new logic where existing code suffices)
`ProcessingPipeline` (`process_data`, `save_windows_embeddings`, `train_model_normal`, `train_model_loo`), `SkeletonExtractor`, `WindowRepository`, `ModelData`, `ModelTrainer`, `SkeletonRepository`, `ChromaClassifier`, `HybridClassifier`, `SkeletonAugmenter`, `tools.config.get_mongo_uri`, `SkeletonEmbedding`.

---

## 9. Edge cases & risks

1. **Embeddings are model-specific** — old embeddings are stale after a retrain; the `embedding_models` membership check + `--force` handle this. Never treat an embedding as permanent across model versions.
2. **Duplicate Chroma entries** — prevented by only embedding `pending`/stale windows; sample ids (`video_id_window_id_idx`) should also be checked before save.
3. **MongoDB availability** — windows come from Mongo; tools must fail fast with a clear message if the DB is unreachable (`get_mongo_uri`).
4. **Class/encoder consistency** — LSTM `label_encoder.classes_`, Chroma `label` metadata, and the `--classes` list must stay in sync; validate trick-name collisions and reserved `transition` up front.
5. **Class imbalance** — balanced weights (default) + optional augmentation; the user decides promotion from `samples-info` numbers, so a too-tiny class can be kept Chroma-only.
6. **Reproducibility** — pin seeds (sklearn/tf/numpy) in the retrain path; record every run in `training_runs` (windows per class, mode, classes, best val acc).
7. **Fine-tune head swap** — `ModelTrainer.fine_tune` must map the existing encoder's classes into the new output head correctly; validate that the existing class order is preserved for the first `n` outputs.
8. **Backfill** — existing window documents need the new fields added before status filtering works; run the migration once.

---

## 10. Backend API integration (summary)

The flow is orchestrated by the future `pole-api` (see `docs/project/pole-api-plan.md`):

1. `POST /api/classes/{id}/crawl` → `pole-crawler` downloads raw videos.
2. `POST /api/classes/{id}/cut` → `VideoCutter` cuts clips (review step: accept/discard).
3. `POST /api/classes/{id}/process` → runs `process-data` (windows → Mongo) then `process-embeddings` (pending → ChromaDB) on the accepted clips.
4. `GET /api/classes/{id}/stats` → surfaces `samples-info` data (embedded/trained/pending counts) so the user can decide.
5. `POST /api/classes/{id}/retrain` → runs the modified `train-model` with the chosen classes and mode when the user decides to promote.

---

## 11. Testing plan

Follow `docs/project/testing-plan.md` conventions (≥80 % coverage maintained; current 89.31 %).
- `tests/test_samples_info.py` — aggregation correctness, JSON/CSV output, label filter.
- `tests/test_train_model.py` — `--classes` filtering, `--mode` dispatch, augmentation/class-weight flags, `training_runs` + window marking.
- `tests/test_model_trainer.py` — new `fine_tune` cases: head swap, class-count change, frozen-encoder path, error when label set is empty.
- `tests/test_process_embeddings.py` — embeds only `pending`/stale windows; marks docs; `--force` re-embeds all.
- `tests/test_storage.py` / `tests/test_window_repository.py` — default fields + status queries/backfill.
- CLI smoke tests: `pixi run samples-info --help`, `pixi run train-model --help`; dry-run flag prints the plan without executing.
- Coverage gate stays `fail_under = 80`.

---

## 12. Rollout / verification checklist

**Implemented (code + tests, coverage gate green):**

- [x] `storage.py` sets `embedding_models`/`training_status` defaults when saving windows (`save_skeleton_data`).
- [x] `window_repository.py` list-based status filters (`get_pending_embeddings`, `get_by_label`), `mark_embedded`, `mark_trained`, `insert_training_run`, `backfill_tracking_fields`.
- [x] `process-embeddings` embeds only windows not yet embedded by the model and appends it to `embedding_models`; `--force` re-embeds all (`save_windows_embeddings(windows, model_path, window_repo, force)`).
- [x] `samples-info` tool (JSON/CSV, `--label`, `--output-format`, `--output`) + pixi task.
- [x] `ModelTrainer.fine_tune(...)` (keep to `feature_vector`, swap head to `n+1`, optional freeze) and `use_class_weight` param in `train`.
- [x] `train-model` CLI: `--mode normal|loo|fine-tune`, `--classes a,b,c`, `--augment N`, `--no-class-weight`, `--reembed|--no-reembed`, `--base-model`, `--epochs`; filters Mongo docs, writes `training_runs`, marks windows `trained`, re-embeds after training.
- [x] Full pytest suite + coverage gate green (538 tests, 89.5% ≥ 80%).

**Manual ops steps (run against live data when promoting a class):**

- [ ] Run the backfill migration to add tracking fields to existing windows.
- [ ] Place accepted clips in `videos/backflip/` → `pixi run process-data --video-dir videos/backflip`.
- [ ] `pixi run process-embeddings` → ChromaDB shows `backflip` label; windows marked `embedded`.
- [ ] Re-run `process-embeddings` → no re-embedding of already-embedded windows (idempotent).
- [ ] `pixi run samples-info` shows `backflip` with embedded/pending/trained counts.
- [ ] Promote: `pixi run train-model --classes handspring,shouldermount,transition,backflip --mode normal` (or `--mode fine-tune --base-model models/lstm_model_normal.keras`) → encoder with 4 classes, model saved, `training_runs` recorded, windows marked `trained`, classes re-embedded.
- [ ] `pixi run evaluate-video` on a held-out backflip clip; `--mode loo` for old+new.
- [ ] Low-data path: `samples-info` shows few samples → keep Chroma-only, no retrain.

---

## 13. Out of scope (future)

- Continuous auto-retraining on every new clip (needs a watcher).
- Automatic promotion heuristics (could be layered on top of `samples-info` later).
- Active-learning sampling of the most confusing new-class clips.
- Moving window storage off MongoDB (Postgres/disk) — the tracking fields assume Mongo stays.
