# Fase 20 — Analysis slice enrichment for Stitch "Pole AI Coach" FE — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md) · Backend endpoints needed by the Stitch design integration in `pole_analyst`

## Contexto

The `pole_analyst` Angular FE is being updated to match the updated Stitch "Pole AI Coach" design.
Two new FE features require backend support that the current analysis slice does not provide:

1. **Analysis History table** — a tabular view of past analyses (video name, date, trick, overall
   score, status). The current `GET /api/analysis/videos` returns only `_id`, `filename`,
   `analyzed`, `created_at`, `updated_at` — it does **not** include `trick_label` or `scores`
   from the `video_histograms` document.

2. **Pose Gallery** — multiple annotated pose frames with skeleton overlays. The current
   `GET /api/analysis/videos/{video_id}/pose` returns exactly **one** frame (the most critical
   detection). The Stitch design shows a gallery of 3+ pose thumbnails that expand to a full
   annotated view with insights.

Both features are read-only extensions of the existing analysis slice. No new collections or
write paths are needed — the data already exists in `analysis-db.video_histograms`.

## Alcance

### 1. Enriched analysis list endpoint

New endpoint `GET /api/analysis/videos/summary` that joins `analysis-db.videos` with
`analysis-db.video_histograms` to return per-video summary data in a single query.

**Response shape:**

```json
[
  {
    "_id": "64f…",
    "filename": "handspring_attempt.mp4",
    "analyzed": true,
    "trick_label": "handspring",
    "overall_score": 75.5,
    "phases": {
      "init": {"start": 0, "end": 25},
      "execution": {"start": 26, "end": 70},
      "exit": {"start": 71, "end": 99}
    },
    "created_at": "2026-08-20T10:00:00Z"
  }
]
```

- `overall_score`: mean of all `scores` values (0-100), or `null` if not yet analyzed.
- `trick_label`: from `video_histograms`, or `null` if not yet analyzed.
- `phases`: from `video_histograms`, or `null`.
- Sorted by `created_at` descending (newest first).
- Supports `skip`/`limit` pagination with `X-Total-Count` header.

### 2. Multi-frame pose endpoint

New endpoint `GET /api/analysis/videos/{video_id}/pose/frames` that returns all detection
frames with their skeleton overlays and issue annotations.

**Response shape:**

```json
{
  "frames": [
    {
      "frame_number": 58,
      "frame_image_path": "/abs/.../frame_58.jpg",
      "phase": "execution",
      "metric": "vertical_speed",
      "z_score": 2.3,
      "issues": [
        {
          "phase": "execution",
          "metric": "vertical_speed",
          "z_score": 2.3,
          "frame": 58,
          "message": "vertical_speed sits above the reference in the execution phase (z=2.31)"
        }
      ]
    }
  ],
  "total_frames": 5
}
```

- Returns all detections from `video_histograms.detections[]` that have a valid `frame_image_path`.
- Sorted by `|z_score|` descending (most deviant first).
- Each frame includes its phase, metric, z_score, and issues.
- `404` when no histogram exists for the video.

### 3. Metric detail data (no new endpoint needed)

The existing `GET /api/analysis/videos/{video_id}/histogram` already returns the full
`resampled` curves needed for the metric detail modal. The FE HistogramTab already consumes
this endpoint. The modal simply renders the same data in a larger view.

## Endpoints (resumen)

| Endpoint | Metodo | Descripcion | Nuevo/Existente |
| :--- | :--- | :--- | :--- |
| `GET /api/analysis/videos/summary` | GET | Enriched list with trick_label + overall_score | **Nuevo** |
| `GET /api/analysis/videos/{video_id}/pose/frames` | GET | Multi-frame pose gallery data | **Nuevo** |
| `GET /api/analysis/videos/{video_id}/histogram` | GET | Full histogram (used by metric modal) | Existente |
| `GET /api/analysis/videos` | GET | Basic list (unchanged) | Existente |

## Architectural Layering

- **Domain:** `AnalysisVideoSummary` (enriched video + histogram join), `PoseFrameGallery` (multi-frame response).
- **Application:** `AnalysisService.get_enriched_list()`, `AnalysisService.get_pose_frames()`.
- **Infrastructure:** `AnalysisVideoRepository` + `AnalysisHistogramRepository` (Mongo aggregation pipeline).
- **Presentation:** `analysis/controllers/videos.py` — two new route handlers.

## Implementation Roadmap

### Phase A: Enriched analysis list
- [ ] Schema: add `AnalysisVideoSummary` Pydantic model to `analysis/schemas.py`.
- [ ] Repository: add `AnalysisVideoRepository.list_with_histograms()` — Mongo aggregation pipeline joining `videos` with `video_histograms` on `video_id`.
- [ ] Service: add `AnalysisService.get_enriched_list(skip, limit)`.
- [ ] Controller: add `GET /api/analysis/videos/summary` route.
- [ ] Tests: unit + integration for the enriched list endpoint.

### Phase B: Multi-frame pose
- [ ] Schema: add `PoseFrameItem`, `PoseFrameGallery` Pydantic models.
- [ ] Service: add `AnalysisService.get_pose_frames(video_id)`.
- [ ] Controller: add `GET /api/analysis/videos/{video_id}/pose/frames` route.
- [ ] Tests: unit + integration for the multi-frame pose endpoint.

### Phase C: Tests + documentation
- [ ] Integration tests against `analysis_db_testing` with seeded video + histogram docs.
- [ ] Update `POLE-API.md` with the new endpoints.

## Quality Gates

- **Unit Tests:** `pixi run test-api` (pytest in `app/pole_api`).
- **Integration Tests:** same suite with `ANALYSIS_DB=analysis_db_testing`.
- **Database Target:** `analysis_db_testing` + `skeleton_data_testing`.
- **Coverage Requirement:** >= 80%.
- **Additional Checks:** `POLE-API.md` updated with the new endpoints.

## Use Cases

### UC-B1: Enriched analysis list (happy path)
- **Given** 3 analyzed videos with histograms in `analysis-db`
- **When** `GET /api/analysis/videos/summary`
- **Then** `200` with array of enriched video docs (trick_label, overall_score, phases)
- **And** sorted by `created_at` descending

### UC-B2: Enriched list with mixed analyzed/unanalyzed
- **Given** 2 analyzed + 1 unanalyzed video
- **When** `GET /api/analysis/videos/summary`
- **Then** `200` with all 3; unanalyzed video has `trick_label: null`, `overall_score: null`

### UC-B3: Multi-frame pose gallery
- **Given** an analyzed video with 5 detections (|z| > 1)
- **When** `GET /api/analysis/videos/{video_id}/pose/frames`
- **Then** `200` with `frames` array of 5 items, sorted by `|z_score|` desc
- **And** each frame has `frame_image_path`, `phase`, `metric`, `z_score`, `issues`

### UC-B4: Pose gallery — no detections
- **Given** an analyzed video with 0 detections
- **When** `GET /api/analysis/videos/{video_id}/pose/frames`
- **Then** `200` with `frames: []`, `total_frames: 0`

### UC-B5: Pose gallery — video not analyzed
- **Given** a video that has never been analyzed
- **When** `GET /api/analysis/videos/{video_id}/pose/frames`
- **Then** `404` `{"detail": "histogram not found"}`

## Risks and Mitigations

- **Risk:** Mongo aggregation pipeline performance on large video sets. **Mitigation:** pagination via `skip`/`limit`; index on `videos.created_at`.
- **Risk:** `frame_image_path` may reference deleted files. **Mitigation:** filter out detections without valid `frame_image_path` in the response.
- **Risk:** FE backward compatibility — existing `GET /api/analysis/videos` is unchanged. **Mitigation:** new endpoint is additive; old endpoint remains for basic library view.

## Open Questions

- None.
