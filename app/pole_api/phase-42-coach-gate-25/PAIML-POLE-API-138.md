# Ticket: PAIML-POLE-API-138

## Title
Training-flow seeding run on LOCAL k3s (all via API): 67 real clips, phase frames, extract/process/embed + LSTM + cohort signals

- **Status**: 📋 PLANNED
- **Project**: pole_api (training slice seeding)
- **Phase**: 42 coach-gate-25
- **Blocks**: —
- **Blocked By**: — independent of 139 (139 backfills `overall_score` on resulting histograms but neither blocks the other).

## Context

USER DECISIONS (binding):

1. **NO mock data, real pipeline only**, all through the API/FE on the **LOCAL
   k3s cluster** (this run is also an end-to-end test of the training slice).
2. **Earlier analyst-API seeding attempt is rejected**: 4 clips seeded via
   `/api/analysis/*` produced hollow results — MediaPipe zero-detections →
   constant metrics — and `overall_score` is never written by any code. Those
   **4 videos + artifacts are to be CLEANED UP** (not the 2 pre-existing August
   mirror docs).
3. **Correct flow is the TRAINING slice (`/api/training/*`)**, whose extractor
   path is proven (1,482 real skeleton windows in backups).
4. **Sources**: `/home/fernando/Proyectos/pole-ai/packages/pole-train-model/sources/videos/`
   = **21 handspring + 25 shouldermount + 21 transition (67 mp4, real footage)**.
5. **Backup phase starts**: `~/.local/share/pole-ai/backups/mongo/20260827_223724/analysis_ai_testing__video_histograms.json`
   carries `phase_frames` (**ENTRANCE/EXECUTION/EXIT**) for **10 handspring +
   4 shouldermount clips, ZERO transition**.

Backup filenames are e2e-synthetic — there is **no 1:1 source link** to the 67
real clips (matching rule below documents the chosen workaround).

## Scope

All steps on the LOCAL k3s cluster, all through the API (no direct DB writes
except verification reads):

0. **Cleanup**: `DELETE /api/analysis/videos/{id}` for the 4 analyst-seeded
   videos + their histograms/landmarks (+ orphan sweep). Leave the 2
   pre-existing August mirror docs untouched. Verify: only 2 mirror docs remain
   before seeding.
1. **`POST /training/classes` ×3**: `handspring`, `shouldermount`,
   `transition`.
2. **`POST /training/classes/{id}/videos`**: upload all **67 clips**
   (21/25/21 per class) from `sources/videos/`.
3. **`PUT /training/clips/{id}/phase-frames` for handspring + shouldermount
   clips ONLY**, sourced from backup `phase_frames` — **matching rule: per-trick
   MEDIAN bounds from backup histograms applied to all clips of that trick**
   (document this choice in the run log: backup filenames are e2e-synthetic, no
   1:1 source link). **Transition clips: no manual phases** (leave for
   auto-detection).
4. **`POST /extract`, `/process`, `/embed` per class**, poll jobs to done.
   **NOTE: in-cluster LSTM training may be SLOW (CPU) — allow long job
   polling** (no short timeouts; poll to done, resumable on disconnect).
5. **Train the LSTM** (in-cluster job flow) + **create/activate classifier**
   (`/models/{run_id}/activate`, verify `/models/chroma`).
6. **Cohort signals** from fresh histograms + phase starts.

## Validation Plan

1. Pre-run: confirm 4 analyst-seeded videos deleted, 2 mirror docs remain
   (`GET /api/analysis/videos` count + IDs).
2. Post-upload: 3 classes with 21/25/21 clips (`GET /training/classes` +
   per-class clip list).
3. Post-extract: **spot-check landmarks non-zero** (real detections). **If zeros
   recur, STOP and file an extraction-parity bug instead of proceeding**
   (do not train on hollow data).
4. Post-embed/train: embeddings present + active classifier present
   (`GET /models/chroma` shows active run).
5. Cohort signals exist for handspring/shouldermount (fresh histograms +
   phase starts readable).

## Acceptance Criteria

- [ ] 4 analyst-seeded videos + artifacts deleted; 2 pre-existing mirror docs intact.
- [ ] 3 training classes with **21/25/21 clips** (67 total, all real footage via API).
- [ ] Phase frames set for handspring + shouldermount clips via per-trick MEDIAN
      bounds rule (choice documented); transition clips untouched.
- [ ] Extract shows **non-zero detections** (landmarks spot-check); zeros →
      STOP + file extraction-parity bug.
- [ ] Embeddings + **active classifier** present (`/models/chroma` verified).
- [ ] Cohort signals exist for handspring/shouldermount.
- [ ] Long-poll tolerance honored (no premature job timeout).

## Dependencies

- **Blocked By**: —.
- **Blocks**: —.

## Estimated Effort

- [L] (67 uploads + CPU-bound in-cluster LSTM; dominated by job wait time)
