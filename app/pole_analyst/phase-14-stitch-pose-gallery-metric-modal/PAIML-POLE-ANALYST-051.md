# PAIML-POLE-ANALYST-051 — PoseGalleryService

## Meta
- **Project:** pole_analyst
- **Phase:** 14 — Stitch Design: Pose Gallery + Metric Detail Modal
- **Status:** TODO
- **Blocks:** — (none)
- **Blocked By:** PAIML-POLE-ANALYST-046

## Description

Create a service that calls the multi-frame pose endpoint and provides the data to the
PoseGalleryComponent, with fallback to the single-frame endpoint.

### Tasks
- [ ] Create `PoseGalleryService` in `core/services/pose-gallery.service.ts`.
- [ ] Implement `getFrames(videoId): Observable<PoseFrameGallery>` method.
- [ ] Use `ApiClientService` for HTTP calls.
- [ ] Fallback: when multi-frame endpoint returns 404, call single-frame endpoint and
      wrap the result in a `PoseFrameGallery` shape.
- [ ] Add unit tests with mock `ApiClientService`.

### Acceptance Criteria
- [ ] Service fetches from `GET /api/analysis/videos/{id}/pose/frames`.
- [ ] Fallback to single-frame endpoint on 404.
- [ ] Returns `Observable<PoseFrameGallery>`.
- [ ] Unit tests pass.
