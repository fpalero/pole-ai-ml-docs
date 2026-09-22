# Instagram Mining for New Tricks — Clustering Plan

> **Status:** Plan (2026-09-22). Agreed inputs: generic entrance/exit heuristic (trick-agnostic),
> high-precision auto-accept + human review of discards, distinct new shapes first (variants later),
> IG `trick_label` known per video (weak label from hashtag/caption).
> **Source code:** `packages/pole-train-model/src/pole_ml|pole_tools`, `app/pole_api/src/analysis/services/phase_detector.py`.
> **Prior RAG:** `docs/tutorials/01|02`, `docs/diagrams/pole_ml|pole_tools|pole_crawler`, `docs/app/pole_api/phase-17-phase-detection/PAIML-POLE-API-046.md`.

---

## 1. Core decisions (from discussion)

1. **Trick = `ENTRANCE + EXECUTION + EXIT`, not execution alone.**
   `[entrance_end, exit_start]` = only `EXECUTION`. LSTM trains on `30x14 stride-5` windows over the
   whole padded clip; histogram/coaching needs `100 pts/phase = 300 pts` (`histogram_processor.py`,
   `histogram_analyzer.resample_by_phase()`). Training on execution-only = distribution shift,
   short clips (`<1.5s` discarded), broken cohort `mean/std`.
2. **`+/-1s` padding is correct for seeding, already the default.**
   `video_cutter.py: video_padding=1.0` → `start_clip = max(0, s-1.0)`. `1s ≈ 30f@30fps = 1 LSTM window`,
   covers detector jitter + `history_window 15 (0.5s)`. Use `[entrance_end-1s, exit_start+1s]` for
   manual/bootstrap cuts; ideal training clip remains `[entrance_start-1s, exit_end+1s]` once full
   boundaries exist. Keep `phase_frames` (unpadded) separate from `clip_boundaries` (padded).
3. **Default `VideoCutter` cannot cut new tricks.** `_detect_target_class_windowed()` requires
   `pred_class == target_class` with `avg>=0.80 open / >=0.65 keep, min_consecutive 5, debounce 1.0s`.
   `HybridClassifier` vocab = old `label_encoder` + Chroma `movement_embeddings` (0 vectors for new
   label) → 0 segments. Padding never runs. Same for trick-specific `PhaseDetector` (Bhattacharyya
   `K=5 sim>=0.7` needs `skeleton_trick_histograms + cohort` for that label → `DESCONOCIDO` for new).
4. **CLIP is the zero-shot semantic gate.** `clip_utils.clip_similarity(frame,labels)->(probs,best)`
   answers `looks like <new shape text>?` with no training. Used in `audit_clips` (3-frame
   `center/right/left`, `thr 0.75 min_hits 2/3`) and `ClipTransitionFilter` (dense `frame_step 2`,
   `target_thr 0.15` + region reconstruct). It does NOT give joints/phases — only keep/discard.
5. **YOLO ≠ LLM replacement.** `YOLO-pose` = alternative to MediaPipe joints; `YOLO detect` =
   person/pole bbox + tracking + pre-filter; `YOLO classify` = still closed-vocab. Only
   `YOLO-World / OWLv2 / Grounding-DINO` (open-vocab + text prompt) overlaps CLIP, as localizer.
   Swapping extractor invalidates `30x14` weights + all `128-d` Chroma vectors → versioned rebuild.
6. **DINOv2 = discovery without prompts.** `384-d` (S) self-supervised frame embeddings cluster
   visually similar unseen shapes before they are named. Complements CLIP (needs prompt) and Chroma
   skeleton (needs label). Separate collection, never mix dims.
7. **IG clips are multi-segment.** One video → N reps of same trick and/or N different tricks.
   Split once (generic), label per segment. Reuse cutter's `detect → transition-filter → duration
   1.5-5.0s → merge gap<=1.5s` + scene-cut guard (never merge across cut / track-ID switch /
   skeleton gap `>0.5s`). Store `parent_video_id + segment_idx` for LOO grouping (reps of one
   video stay in same fold).
8. **IG label = proposal, cluster = verification.** Per-label clustering: keep largest cohesive
   cluster as canonical, outsiders → human queue (never silent-delete, never train on unfiltered
   label set — one mislabel shifts cohort `mean`, inflates `std`, kills `PhaseDetector`).

---

## 2. Architecture

```
IG crawler (InstagramClient + DiskWriter/PostMetadata + QC res/fps/duration)
 -> person/pole pre-filter (YOLO-World, 1 person+1 pole >80% frames, stable track ID)
 -> SkeletonExtractor VIDEO mode + hip-center/shoulder norm + visibility>=0.7
 -> generic proposal: 20f/stride-5 (or 30/5) windows, M-01..M-05 derivatives,
    entrance_end = motion onset, exit_start = return to baseline (STATIC/SPIN/MOMENTUM heuristics)
 -> per-segment cut [entrance_end-1s, exit_start+1s] via pole_crop ffmpeg
    + duration 1.5-5.0s + merge<=1.5s + scene-cut guard
 -> precision gate (no LSTM/Chroma yet):
    SigLIP2/CLIP 3-frame audit (auto-keep >=0.75 2/3 hits; queue 0.5-0.75; discard <0.5)
    + ClipTransitionFilter region trim (transition_ratio>0.3 discard)
 -> DINOv2 per-label clustering (mean-pool 3-5 exec frames, L2-norm, HDBSCAN cos)
    keep core cluster, queue outsiders
 -> accepted -> process_data (30x14 s5 windows + 300-pt hist) -> process_embeddings (128-d)
              samples_info balance -> LOO + augment mirror/timing/perturb
              -> fine_tune additional_classes=1 / scratch -> approve/activate (human gate B9)
 -> discards/low-cohesion -> FE Manual Phases Modal -> phase_frames + selected_for_training
 -> once N>=5 segs across >=2 videos: build skeleton_trick_histograms (8 bins [-3,1])
    + cohort mean/std ddof=1 -> enable PhaseDetector K=5/0.7 + chroma-only cutter (0.75/0.50)
```

---

## 2b. Detailed pipeline (step by step)

Each step lists purpose, in/out, where it lives, params, and done-check.
IG weak `trick_label` flows through as proposal only; visual verification decides keep/queue.

### Step 0 — Crawl + ingest + weak label
- **Do:** `InstagramClient + make_session` fetch by account/hashtag; `DiskWriter` saves
  `video.mp4 + PostMetadata {post_url, caption, hashtags, trick_label_guess, fps, res, duration}`.
  Parse `trick_label` from hashtag/caption map (`aliases.py`); mark `label_source=ig_weak`.
- **QC in:** `res>=720p short-side, 0.5s<=dur<=90s, fps>=24, non-empty, has audio/video streams`.
  Dedup by `post_id`; near-dedup later by DINO `cos>0.95`.
- **Out:** `raw_ig/{trick_label}/{post_id}.mp4 + .json`.
- **Code:** `packages/pole-crawler/`, `docs/diagrams/pole_crawler/FLOW.md`.
- **Done when:** `ls raw_ig/<label>/*.mp4` counted + manifest written; 429/session-rot handled with waits.

### Step 1 — Extract background / localize person+pole
- **Why first:** DINO/CLIP/skeleton all fail on IG background (audience, studio colour, 2nd person).
  Crop to athlete before anything expensive.
- **Do:**
  1. `YOLO-World (or Grounding-DINO) prompt=["pole dancer","pole"]` per sampled frame
     (`every 5th frame`, `conf>=0.5`).
  2. Track main athlete by `IoU>0.5` across frames → stable `track_id`; require
     `1 person + 1 pole in >80% sampled frames`, else `queue(no-subject)`.
  3. Scene-cut detect: `frame-diff spike or track-ID switch or embedding jump` → split timeline,
     never merge across cut later.
  4. Build `person_crop (bbox +10% pad, square-pad to 1:1)` per segment; export two variants:
     `crop_clean.mp4` (tight crop) for skeleton/DINO, plus `crop_blur.mp4`
     (person sharp, background `Gaussian blur r=21` / gray) for DINO/CLIP to kill studio bias.
  5. Save `localization.json {bboxes, track_id, cuts:[t], keep_ratio}`.
- **Out:** `crops/{post_id}/crop_clean.mp4, crop_blur.mp4, localization.json`.
- **New code:** `pole_ml/filters/person_localizer.py` (no change to `30x14` contract).
- **Params:** `sample_every=5, det_conf=0.5, keep_ratio=0.8, pad=0.10, blur_r=21`.
- **Done when:** fixture IG set shows `visibility mean +15%` and DINO no longer clusters by wall colour
  (check UMAP before/after).

### Step 2 — Skeleton extraction (pose, trick-agnostic)
- **Do:** `SkeletonExtractor` MediaPipe `PoseLandmarker VIDEO` on `crop_clean.mp4` with monotonic
  `timestamp_ms`; `normalize = hip-center + shoulder-width`; `_filter_by_visibility >=0.7`;
  `extract_biomechanical_features -> 14/frame`; keep `landmark_frames {frame,timestamp,landmarks,
  visibility_count}` + `features_history [(t, 14-vec)]`.
- **Fallback:** frames with `landmarks=None` → `zeros(14)` + `visibility 0`; gap `>0.5s` of Nones =
  hard boundary (cut here, never merge).
- **Code:** `pole_ml/processors/skeleton_extractor.py`, `processing_pipeline.extract`.
- **Done when:** `avg_visibility` logged per clip; clips with `<50%` visible frames → `queue(pose-bad)`.

### Step 3 — Generic entrance/exit proposal (no references)
- **Do:** sliding windows `20f/stride-5` (PhaseDetector geometry) over M-01..M-05
  (`angular_speed, torso_tilt_speed, wrist_stability rolling w=5, hip_height, body_tilt`);
  `entrance_end = motion onset` (e.g. `|angular|`/`d_hip` rise above STATIC band),
  `exit_start = return to baseline`; reuse `classify_trick` bands
  (`spin_ratio>0.5, early d_hip>3.0, static_ratio>0.7`) only to pick family thresholds, not label.
  Output `proposals [(e_end, x_start, conf)]` per continuous motion event between cuts/gaps.
- **Multi-seg:** one IG video → N proposals (reps + mixed tricks); do NOT classify yet.
- **New code:** `pole_ml/processors/generic_phase_proposer.py`.
- **Done when:** runs on unseen shapes with zero `skeleton_trick_histograms`; recall-first
  (better extra proposal than missed rep).

### Step 4 — Cut with +/-1s
- **Do:** per proposal cut `[e_end-1.0s, x_start+1.0s]` via `pole_crop ffmpeg crop_segment`
  (`-ss/-to` lossless); clamp `[0, dur]`; record unpadded `[e_end,x_start]` as provisional
  `phase_frames.EXECUTION` + padded as `clip_boundaries (path,s_clip,e_clip,parent_video_id,seg_idx)`.
- **Params (YAML-tunable per family):** `video_padding=1.0, shift_start=0, shift_end=0`
  (`1s ≈ 30f@30fps = 1 LSTM window`; covers jitter + `history 15`).
- **Code:** `pole_tools/cli/video_cutter._extract_clips`, `pole_tools/services/crop.py`.
- **Done when:** `>=80%` padded clips have `>=3 windows (30x14 s5)`; `1.5s<=clip<=5.0s` else flag.

### Step 5 — Per-segment QC + de-merge guard
- **Do:** drop/queue if `dur<1.5 or >5.0`, `avg_visibility<0.5`, `no-subject`, gap-crossing;
  merge only if `gap<=1.5s AND same track_id AND no scene-cut AND no skeleton-gap`;
  `debounce 1.0s` to avoid double-count holds.
- **Out:** `segments_qc.json` with `keep/queue/discard + reason`.
- **Done when:** `handspringx3 + handspring+shouldermount` fixture → 3 clips and 2 clips respectively,
  no mixed clip.

### Step 6 — Zero-shot precision gate (CLIP/SigLIP, no LSTM)
- **Do:**
  a. `audit`: `labels=[f"a pole dancer doing {ig_label}"]+3x transition ("climbing or spinning",
     "moving between moves","neutral position")`; 3 frames `center/right/left` on `crop_blur.mp4`;
     `auto-keep if >=2/3 hits conf>=0.75`; `queue if 0.5-0.75 or 1/3`; `discard if <0.5`
     (`--prompt` override per new shape).
  b. `ClipTransitionFilter` dense `frame_step 2, target_thr 0.15`: per-frame
     `target_conf=sum(target)/sum(all)`, region reconstruct, drop region if
     `transition_ratio>0.3 or target_ratio<0.4`.
- **Code:** `pole_ml/filters/clip_utils.clip_similarity`, `cli/audit_clips.py`,
  `filters/transition_filter.ClipTransitionFilter`.
- **Done when:** precision-first on IG fixture; every discard has `{reason, probs, frame}`.

### Step 7 — DINOv2 embedding (discovery vector)
- **Do:** `dinov2_vits14` lazy-load (`DINO_DEVICE=cpu|cuda`); per kept segment sample 3-5 exec
  frames from `crop_blur.mp4`; `518px → 384-d → L2-norm`; per-clip vector = mean-pool + renorm.
  Save to parallel Chroma `image_dino_embeddings (cosine, 384-d)` with
  `{video_id, parent_video_id, seg_idx, clip_path, frame_idxs, ig_label}`. Never mix with
  `movement_embeddings (128-d skeleton)`.
- **New code:** `pole_ml/processors/dino_embedding.py` mirroring `skeleton_embedding.py`.
- **Done when:** unit `dim 384 norm 1.0`; `10xA+10xB` fixture `ARI>0.8`.

### Step 8 — Per-label clustering (IG label = proposal, cluster = verdict)
- **Do:** group by `ig_label`; dedup `cos>0.95`; `HDBSCAN(min_cluster_size=5, min_samples=3,
  metric=cosine)` → `{cluster_id,size,members,centroid,medoid_thumb,silhouette}` + UMAP plot.
  Canonical = largest cluster with `silhouette>0.4`; `cos_to_centroid>=0.75` auto-keep;
  `0.55-0.75` or second `size>=3` cluster → queue (possible variant); else discard.
  Write `cluster_id` back to Chroma metadata + `clusters/{ig_label}.json` with thumbnails.
- **New code:** `pole_tools/cli/cluster_dino.py`.
- **Done when:** tagged-`X` video containing `X+Y` → X segs kept, Y segs queued as outsiders;
  reps `x3` all kept with shared `parent_video_id`.

### Step 9 — Human review queue (discards + low-cohesion)
- **Do:** FE queue shows `clip + center thumb + probs + cos_to_centroid + reason + UMAP position`;
  reviewer sets `phase_frames {ENTRANCE,EXECUTION,EXIT}`, `trick_label` correct/new, and
  `selected_for_training true/false`. Manual Phases Modal is the only writer of `phase_frames`
  (auto-detection stays removed per `PAIML-POLE-AGENT-015`).
- **Out:** `reviewed.json`; feeds Steps 10-11.
- **Done when:** every queued item resolved; reasons taxonomy logged for threshold tuning.

### Step 10 — Promotion to LSTM + references (canonical only)
- **Do:** ONLY canonical-cluster segs with `selected_for_training`:
  `process_data (Biomechanical 30x14 s5 + Histogram 300-pt)` → `samples_info` balance →
  `process_embeddings (bottleneck 128-d → movement_embeddings)` →
  `upsert_trick_histograms (8 bins [-3,1]) + upsert_cohort_statistics (mean/std ddof=1,
  sigma_floor guard)` (require `N>=5 segs, >=2 videos`) →
  `train_model LOO + class_weights + augment mirror/timing/perturb` or
  `fine_tune additional_classes=1 freeze_base` → `evaluate` per-class gate →
  `approve/activate` human gate (B9). LOO folds grouped by `parent_video_id`.
- **Code:** `cli/process_data|process_embeddings|train_model|samples_info`, `ModelPersistence run_id`.
- **Done when:** new shape is trainable class; `HybridClassifier lstm_thr 0.7` + Chroma fallback live.

### Step 11 — Recall loop (now trick-specific works)
- **Do:** flip mining to `VideoCutter classifier_mode=chroma (high 0.75/low 0.50)` +
  `ChromaDBTransitionFilter (0.40)` and `PhaseDetector.detect (window 20 s5 K=5 sim>=0.7)` for
  full `ENTRANCE/EXECUTION/EXIT` boundaries. Variants specialization starts here.
- **Done when:** recall gain on held-out IG videos without precision drop; thresholds versioned.

---

## 3. Roadmap

### Phase A — Generic split + padding (bootstrap)
- [ ] Generic proposer module (motion onset/offset on `angular_speed, hip_height, body_tilt`,
      `wrist_stability rolling w=5`); outputs `[entrance_end, exit_start]` + confidence.
- [ ] Cutter wrapper: cut `[e-1s, x+1s]`, `video_padding`/`shift_start`/`shift_end` YAML-tunable per
      trick family; emit `clip_boundaries (path,s,e)` + `parent_video_id`.
- [ ] Guards: duration, merge, debounce, scene-cut/track-switch veto, visibility mean.
- Accept: proposer runs on unseen shapes with no references; padded clips `>=3 windows` majority.

### Phase B — Zero-shot precision gate (CLIP/SigLIP)
- [ ] `audit` step: `labels=[target_prompt]+3x transition`, `thr 0.75 min_hits 2/3` auto-keep,
      `0.5-0.75` queue, `<0.5` discard; custom prompt per new shape allowed (`--prompt`).
- [ ] `ClipTransitionFilter` as region trimmer (`target_thr 0.15 frame_step 2` start).
- Accept: IG fixture set → precision-first; all discards land in review queue with reason.

### Phase C — Person/pole localization (YOLO-World)
- [ ] Pre-filter + crop before skeleton/CLIP (kills audience/background false positives, fixes
      `visibility<0.7` drops). No extractor swap yet.
- Accept: kept-frame rate + visibility gain on IG sample; no change to `30x14` contract.

### Phase D — DINOv2 per-label cluster verification
- [ ] `dino_embedding.py` (lazy `dinov2_vits14`, 384-d L2-norm, `DINO_DEVICE` env) + Chroma
      `image_dino_embeddings (cosine)` parallel to `movement_embeddings`; metadata
      `{video_id, clip_path, frame_idx, cluster_id}`.
- [ ] `cluster-dino` CLI: per-label mean-pool → dedup `cos>0.95` → `HDBSCAN(min_cluster_size=5,
      min_samples=3, cosine)` → `{cluster_id,size,members,centroid,silhouette,thumbnails}` +
      UMAP plot; canonical = largest `silhouette>0.4` cluster.
- [ ] Person-crop + background-blur before embed (else clusters = studio/clothing).
- Accept: `10x handspring + 10x shouldermount` fixtures → 2 pure clusters `ARI>0.8`; new IG label
      → core kept, Y-mix/outliers queued.

### Phase E — Promotion to LSTM + references
- [ ] `process_data → samples_info → process_embeddings → train/fine-tune (LOO, class weights,
      augment) → approve/activate`; LOO groups by `parent_video_id` (no rep leakage).
- [ ] Build `skeleton_trick_histograms + cohort` only from canonical cluster (`N>=5, >=2 videos`);
      single-video `std=0` guarded by `sigma_floor`.
- [ ] Flip Stage B to `chroma-only cutter (0.75/0.50)` + trick-specific `PhaseDetector` for recall
      mining. Variants specialization starts here.
- Accept: new shape reaches trainable class with per-class metrics gate; `Hybrid 0.7` fallback live.

---

## 4. Thresholds (defaults, tune per family)

| Where | Param | Default |
|---|---|---|
| LSTM windows | `30x14, stride 5` | fixed contract |
| PhaseDetector | `window 20 stride 5 K=5 sim>=0.7` | `phase_detector.py` |
| Cutter hybrid | `high 0.80 / low 0.65, history 15, min_consec 5, debounce 1.0s` | `video_cutter.py` |
| Cutter chroma-only | `high 0.75 / low 0.50, chroma_thr 0.40, target_ratio>=0.4, trans_ratio<=0.3` | same |
| Clip geometry | `min 1.5s / max 5.0s, padding 1.0s, merge gap<=1.5s` | same |
| Skeleton QC | `visibility>=0.7` | `SkeletonExtractor` |
| CLIP audit | `thr 0.75, min_hits 2/3` | `audit_clips.py` |
| CLIP transition | `target_thr 0.15, frame_step 2` | `_build_clip_transition_filter` |
| DINO cluster | `HDBSCAN min_size 5 / min_samples 3 / cosine, dedup 0.95, keep cos>=0.75` | Phase D |
| Promotion | `>=5 segs, >=2 videos, silhouette>0.4` | Phase E |

---

## 5. How to do each step (implementation detail)

### Step 0 — How to crawl + label
1. `make_session(cookies: sessionid/csrftoken)` → `InstagramClient.fetch(target, limit)` with
   anti-bot waits (`sleep 2-5s`, backoff on 429). Save `DiskWriter.write(post_id.mp4, PostMetadata)`.
2. Parse label: lowercase caption+hashtags → `aliases.py` map (`#handspring→handspring`,
   `#pdhandspring→handspring`, unknown tag → `ig_label=raw_tag`, `label_source=ig_weak`).
3. QC script (`ffprobe`): reject `short_side<720`, `fps<24`, `dur<0.5 or >90s`, `size==0`.
   Manifest: `raw_ig/manifest.jsonl` one row per post `{post_id, ig_label, path, fps, dur}`.
4. Run: `pixi run crawl -- --target <account|tag> --out raw_ig/`.

### Step 1 — How to extract background / localize
1. Sample every 5th frame via `cv2.VideoCapture` (same pattern as
   `video_cutter._detect_target_class_windowed`, `audit_clips.auditar_un_clip`).
2. Detect: `YOLO-World(texts=["pole dancer","pole"], conf>=0.5)` → `boxes[x1,y1,x2,y2]`.
   If only `ultralytics YOLOv8` available, use `yolov8m.pt person(0)` + pole as largest vertical
   line/box near person; upgrade to World later — interface stays `detect(frame)->boxes`.
3. Track: greedy IoU `>0.5` to previous main box; new ID on switch. Log `cuts[]` when
   `mean(|frame_t-frame_{t-1}|)>thr` OR track switch OR `skeleton None-gap>0.5s` starts.
4. Crop: `square = max(w,h)*1.10`, clamp to frame, `cv2.getRectSubPix`/resize to `512px` short side.
   Write `crop_clean.mp4` (`mp4v, same fps`). Then `crop_blur.mp4`: person mask = box interior sharp,
   exterior `cv2.GaussianBlur(21,0)` (or gray `0.5`). Reuse `pole_crop/ffmpeg.crop_segment` for
   re-encode so timestamps stay aligned with clean.
5. Gate: `keep_ratio = frames_with(1 person and >=1 pole)/sampled`; `<0.8 → queue(no-subject)`.
6. New file `pole_ml/filters/person_localizer.py`: `localize(video)->(clean,blur,localization.json)`;
   mirror `clip_utils.py` lazy-load (`_lazy_yolo()`, `YOLO_DEVICE` env).

### Step 2 — How to extract skeleton
1. Call `SkeletonExtractor(model_path).extract_skeleton_sequence(crop_clean.mp4, stride=1)` for
   proposal density (stride 5 only for LSTM windows later). `reset()` per video (monotonic-timestamp
   bug: one instance per video).
2. Per frame: `normalize_coordinates` (hip-center 23/24, scale shoulder-width 11/12) →
   `_filter_by_visibility(>=0.7)` → `extract_biomechanical_features -> 14 vec` or `None`.
   Persist `landmark_frames + features_history` (same shape `video_cutter` builds inline).
3. Metrics for Step 3 reuse `HistogramDataProcessor.compute_metrics(landmark_frames)` →
   `{angular_speed (unwrapped azimuth d/dt), torso_tilt_speed, wrist_stability rolling_std w=5,
   hip_height, body_tilt}`. Do NOT need `phase_frames` here.

### Step 3 — How to propose entrance/exit generically
1. Window `20f/stride-5` over metric series (PhaseDetector geometry `WINDOW_SIZE=20, STRIDE=5`).
2. Per window compute `mean|angular|, max(d_hip), mean|tilt_speed|`; onset when 2/3 exceed family
   bands (start from `classify_trick` bands: `|angular|>2.0 ratio, d_hip>3.0 early, static<0.5`).
   Require `K=5` consecutive onset windows (same consensus as `REQUIRED_MATCHES=5`) → `e_end=t_first`.
   Offset symmetric → `x_start=t_last` of return-to-baseline run. Confidence =
   `fraction_of_windows_above_band * visibility_mean`.
3. Split on `cuts[]`/track-switch/`None-gap>0.5s` first; never propose across them.
4. Output `proposals.json [{e_end_s, x_start_s, conf, family_hint}]`. Tune bands per
   STATIC/SPIN/MOMENTUM later; start single global set, recall-first.

### Step 4 — How to cut with +/-1s
1. For each proposal: `s=max(0,e_end-1.0+shift_start)`, `e=min(dur,x_start+1.0+shift_end)`.
   `ffmpeg -ss <s> -i in -t <e-s> -c:v copy -c:a copy out` (same as `_extract_clips`);
   re-encode only if cut not keyframe-accurate (`-c:v libx264 -crf 18` fallback).
2. Name `"{post_id}_{ig_label}_{idx}.mp4"`; write `clip_boundaries.json` +
   provisional `phase_frames={EXECUTION:[e_end,x_start]}` (ENTRANCE/EXIT filled at review).
3. Verify `dur 1.5-5.0s` and `n_windows=((n_frames-30)//5)+1 >=3` else flag `too-short`.

### Step 5 — How to QC + guard merges
Apply in order per `video_cutter.process_video`: transition-trim → duration filter → merge
(`gap<=1.5s` AND `same track` AND `no cut` AND `no skeleton gap`) → duration re-filter.
Emit `segments_qc.json {clip, verdict, reason}`. Fixture test: `3x repeat → 3 clips`,
`A+B mixed → 2 clips, no mixed`.

### Step 6 — How to run the CLIP gate
1. Audit (sparse): `clip_similarity(bgr, [target]+3x_transition)` on `center, 3/4, 1/4` frames of
   `crop_blur.mp4` (exact `auditar_un_clip` order + dedup + clamp). `target_conf=probs[0]`,
   hit if `>0.75 and best==0`; `hits>=2 → keep`, `==1 or max in [0.5,0.75) → queue`,
   else discard. Log `{probs, frame, ts}` per sample.
2. Trim (dense): `ClipTransitionFilter(frame_step=2→10 for speed, target_thr=0.15)`:
   `target_agg=sum(probs[:n_target])`, `conf=target_agg/sum(all)`, `is_valid=conf>thr and best<n_target`;
   reconstruct contiguous valid regions (same code as `ChromaDBTransitionFilter`), drop region if
   `transition_ratio>0.3 or target_ratio<0.4`. This shortens paddings that bled into transitions.
3. Swap `open_clip ViT-B-32` → `SigLIP2-B/16` later by only changing `CLIP_MODEL_NAME/PRETRAINED`
   env + `clip_utils._lazy_clip()`; callers unchanged.

### Step 7 — How to embed with DINOv2 (3-5 mean-pool frames in detail)
1. Load once: `torch.hub.load('facebookresearch/dinov2','dinov2_vits14')` (or HF
   `facebook/dinov2-small`), `.eval().to(DINO_DEVICE)`, `torch.no_grad()`. Preprocess:
   `Resize(518) CenterCrop(518) Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])`
   on RGB (BGR→RGB first, same as `clip_encode_image`).
2. Frame pick per kept clip (from `crop_blur.mp4`, total `F` frames):
   - Let `a = int(0.2*F)`, `b = int(0.8*F)` = middle 60% (execution core; skips padded
     entrance/exit edges where transitions live).
   - If `F>=5`: idxs `[a, (a+b)//2 - step, (a+b)//2, (a+b)//2 + step, b]` with dedup+clamp
     (mirrors `auditar_un_clip` candidate dedup); if `3<=F<5`: use all; if `F<3`: reject clip.
   - Default `k=5`, minimum `k=3`. Read via `cap.set(PROP_POS_FRAMES, i)`, skip `ret==False`.
3. Embed each → `v_i (384-d)` → `v_i/=||v_i||`. Clip vector `c = mean(v_i)` → `c/=||c||`.
   Mean-pool averages out pose jitter; renorm puts all clips on the unit sphere so Chroma
   `cosine` = dot product. Log per-frame `||v||` pre-norm (all-zero/NaN → skip frame).
4. Store: Chroma `get_or_create_collection("image_dino_embeddings", {hnsw:space:cosine})`,
   `add(ids=[f"{parent_video_id}_{seg_idx}"], embeddings=[c.tolist()], metadatas=[{ig_label,
   clip_path, frame_idxs, fps, blur:true}])`. Separate client/persist subdir from
   `movement_embeddings` (different dim). Mirror `SkeletonRepository.save()` + pending/force logic.
5. New file `pole_ml/processors/dino_embedding.py`: `DinoEmbedding(model="vits14").embed_frames(
   frames)->c`, `embed_clip(clip_path, k=5)->(c, idxs)`; batch stacking for GPU when available.
6. Unit checks: `c.shape==(384,)`, `||c||≈1.0`, same clip twice → `cos>0.99`, blurred vs clean same
   clip → `cos>0.9` (else crop leaking).

### Step 8 — How to cluster per label (in detail)
1. Pull per `ig_label`: `X = [c_1..c_N]` (already L2-normed) from `image_dino_embeddings`.
2. Dedup: pairwise `cos = X@X.T`; greedily drop `j>i` with `cos>0.95` (same repost/crop).
   Keep `dedup_map` for counts.
3. Cluster: `hdbscan.HDBSCAN(min_cluster_size=5, min_samples=3, metric='euclidean')` on unit
   vectors (= cosine distance). Why: unknown #shapes, noise label `-1` built-in, matches promotion
   gate `>=5`. If `hdbscan` missing, fallback `sklearn.cluster.AgglomerativeClustering(
   n_clusters=None, distance_threshold=0.35, metric='cosine', linkage='average')`.
4. Centroid/medoid/stats per cluster `C`: `centroid = mean(X_C)` renorm; `sims = X_C@centroid`;
   `medoid = argmax(sims)` (real thumb, not average); `cohesion=mean(sims)`;
   `silhouette_samples(X, labels, metric='cosine')` → `silh_C=mean` (needs `>=2` clusters, else
   use cohesion only); `size=len(C)`.
5. Decide: canonical = largest `size>=5 and (silh>0.4 or cohesion>=0.75)`; members with
   `sim>=0.75 → keep`, `0.55-0.75 → queue`, `<0.55 → outsider/queue`. Second cluster `size>=3`
   → `queue(variant-candidate)` (future variant track). Noise `-1` → queue individually.
6. Write back: `collection.update(ids, {cluster_id, sim_to_centroid, verdict})` +
   `clusters/{ig_label}.json {centroid, members:[{clip, sim, thumb_frame}], umap.png}`.
   UMAP (`n_neighbors=15, min_dist=0.1, metric='cosine'`) only for FE plot, never for decisions.
7. New CLI `pole_tools/cli/cluster_dino.py --label <ig> --min-size 5`: prints
   `label N=.. kept=.. queued=.. silh=..`; `--save-json` + `--thumbs` (extract medoid + 2 nearest
   via `extract_frame`, same helper as `HistogramAnalyzer` critical-frame export).
8. Done-check on fixture: `10xA+10xB → 2 clusters ARI>0.8`, tagged-X-with-Y → X kept / Y outsiders.

### Step 9 — How to review
FE row = `looping clip + medoid thumb + CLIP probs + sim_to_centroid + UMAP dot + reason`.
Actions: `keep+phase_frames / relabel / variant-split / reject`. Writes
`videos.phase_frames + selected_for_training` (only writer). Export `reviewed.json` for audit.

### Step 10 — How to promote (canonical only, exact commands)
1. `python -m pole_tools.cli.process_data --video-id <id>...` (Biomech `30x14 s5` + Hist `300-pt`;
   fails closed on missing `phase_frames`).
2. `samples-info --label <new>` → assert `videos>=2, windows/video>=3`, balance vs old classes.
3. `python -m pole_tools.cli.process_embeddings --model <run.keras>` → `128-d → movement_embeddings`.
4. `upsert_trick_histograms` (8 bins `[-3..1]`) + `upsert_cohort_statistics` (`ddof=1`, `sigma_floor`).
5. `train_model (--fine-tune base --additional-classes 1 --freeze-base)` or scratch; LOO grouped by
   `parent_video_id`; `evaluate` per-class gate; `approve/activate` human click (B9).

### Step 11 — How to flip to recall
`VideoCutter(classifier_mode='chroma', high=0.75, low=0.50, transition='chroma 0.40')` +
`PhaseDetector.detect(window=20, stride=5, K=5, sim>=0.7)` for full 3-phase bounds.
Compare kept-count + precision vs Step 6-8 on held-out IG set; version thresholds in YAML per family.

---

## 6. Risks

* Generic thresholds tuned on known tricks miss new dynamics (static holds vs momentum peaks) →
  keep proposer conservative (high recall) + CLIP/DINO as precision.
* Fixed `1s` under-covers long spin-ups, over-covers exits, bleeds adjacent tricks in compilations →
  per-family `video_padding` + scene-cut veto + transition trim.
* IG label noise (wrong hashtag, multi-trick video) → never `upsert_trick_histograms` pre-cluster.
* Background bias in DINO (studio/clothing) → person-crop mandatory; validate with ARI fixture.
* Extractor swap (MediaPipe→YOLO-pose) invalidates all weights/embeddings → treat as versioned
  rebuild, not incremental change.
