# Ticket: PAIML-POLA-API-037

## Title
[Infrastructure] Clip-scoped `extracted` / `histo` counts in `count_by_status` + `list_videos`

## Description
Phase 14 (§10.3.2, D-3 — PO confirmed 2026-08-13). Extend the counts the FE already receives via the
`X-Count-*` headers on `GET /api/training/classes/{id}/videos` with `extracted` and `histo` buckets,
scoped to the same `clip` filter as the listing, so both the Videos and Clips tabs show accurate
filter-pill counts (`NEW EXTRACTED PROCESSED HISTO READY`). No new endpoint, no route change.

## What to Do (Implementation Steps)
- [ ] `VideoRepository.count_by_status(class_id, clip: bool | None = None)`: add
      `"extracted": count_documents({**query, "extracted": True})` and
      `"histo": count_documents({**query, "histogram_processed": True})`; apply
      `_apply_clip_filter(query, clip)` when `clip is not None`. Default `clip=None` must preserve the
      current non-clip behaviour (regression safety).
- [ ] `ProcessService.list_videos`: thread the incoming `clip` argument into `count_by_status` so a
      `?clip=true` listing returns clip-scoped counts and a `?clip=false` (or absent) listing returns
      non-clip counts. The existing `X-Count-{key}` header loop in
      `training/controllers/process.py` then exposes `X-Count-extracted` / `X-Count-histo` automatically.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `GET /api/training/classes/{id}/videos?clip=true` returns `X-Count-extracted` and
      `X-Count-histo` matching `count_documents` over the same clip filter.
- [ ] The legacy `count_by_status(class_id)` call (no `clip`) returns the same `all/new/processed/ready`
      buckets as before (plus the additive `extracted`/`histo`).

## Integration Tests to Run (Local Verification)
- [ ] UC-101 from `docs/app/pola_api/PLAN.md` §10.5; existing `test_process*.py` stay green.

## Dependencies
- **Blocks**: PAIML-POLA-API-038
- **Blocked By**: PAIML-POLA-API-036

## Estimated Effort
- [S]
