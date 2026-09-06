# Theme 01 — Skeleton & Pose · Audience: Full-Stack / Backend Engineers

> Backend engineers integrating pose/ML into services. Focus: the contracts,
> the data flow, and the production bugs — not the math.

## Catalog

### A1 (adapted) — Serving Pose Extraction Behind an API
- **Difficulty:** Intermediate
- **Type:** Integration tutorial
- **Hook:** "The ML side gives you landmarks; your job is the pipeline that turns them into stored, queryable data."
- **Description:** How the extraction layer fits under a backend: video → frames
  → normalized landmarks → persisted with progress tracking and indexing; the
  auto-embed-on-upload flow (upload → process → clips) exposed as jobs. Great
  for engineers wiring ML components into FastAPI/worker slices.
- **Grounding:** `docs/packages/pole_ml/IMPLEMENTATION_SUMMARY.md`,
  `docs/app/pole_api/plan/PLAN_PHASE_5.md`.
- **Sellable angle:** Bridges CV and backend; job-queue patterns for video work.

### A2 — The "Monotonically Increasing Timestamp" Bug
- **Difficulty:** Beginner → Intermediate
- **Type:** Debugging case study
- **Hook:** Shared state between workers broke the extractor — a classic
  backend bug wearing a CV costume.
- **Description:** The same timestamp bug retold from a backend perspective:
  instance reuse across files, reset() discipline, one extractor per video in
  long-running cutters.
- **Grounding:** `docs/packages/pole_ml/project/Improvements.md` (A5).
- **Sellable angle:** Relatable bug story; cheap to produce (already written up).