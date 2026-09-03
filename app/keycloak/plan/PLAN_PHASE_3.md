# Plan Phase 3 — Temp-User Data Isolation & Expiry Purge

> **Parent plan:** [PLAN.md](../PLAN.md)
> **Status:** ✅ DONE

## Scope

Guarantee a temporary user's data is fully isolated and **completely removed** when their access expires. Per the product decision, a temp user **cannot share data with anyone** — on expiry we delete **every** resource the temp user created (including shared/global ones), then disable the Keycloak user. The account is kept only for audit; the Redis 14-day cooldown prevents re-request.

## Context

Most slices already scope by `owner_id` (the Keycloak `sub`). Reusable deletion logic already exists: `video/services/video_deletion_service.py` (videos, clips, files, `skeleton_windows`, Chroma embeddings, class cascade) and `analysis` repositories with cascade deletes (video, histogram, landmarks). This phase adds a purge path keyed by the temp user's `owner_id`.

## Tasks

### Ownership audit
- [ ] [Application] Audit that every temp-user-created resource persists `owner_id` (Keycloak `sub`): videos, clips, uploads, analysis videos/histograms/landmarks, athlete profile, crawler posts/images, training classes, model runs, chatbot sessions.
- [ ] [Application] Identify any resource created without `owner_id` that a temp user could touch; backfill the field on write for temp users.

### Purge job
- [ ] [Application] `core/temp_access.py` — `TempAccessPurgeService` driven by `owner_id`: enumerate all owned resources and delete them via the **existing** services (reuse `VideoDeletionService`, `AnalysisService.delete_video`, crawler post/image deletion, profile delete, class cascade, chroma/window deletion) rather than re-implementing.
- [ ] [Application] Delete physical files on the PVC (uploads, analysis_uploads, curated, downloads, chroma) referenced by the owned resources.
- [ ] [Application] Delete Redis chatbot sessions and any `temp:*` keys for the email.
- [ ] [Application] Disable the Keycloak user (kept for audit) via the admin client.
- [ ] [Application] Option 2 semantics: also delete shared/global resources the temp user created (classes, curated clips, model runs) so no temp-created data remains.

### Expiry triggering
- [ ] [Application] Sweeper: periodic task (interval < window) that finds expired `temp:active:{email}` keys, runs the purge, then disables the user.
- [ ] [Application] Lazy expiry: on any authenticated request for a temp email whose `temp:active` key has expired, trigger the purge (defense in depth alongside the 2h token `exp`).
- [ ] [Application] Idempotency: purge is safe to re-run; already-deleted files/docs are skipped.

## Dependencies

- Phase 2: `temp:active` keys, admin client `disable_user`, token `exp`.
- Existing deletion services (`video_deletion_service.py`, analysis cascade deletes).

## Acceptance Criteria

- [ ] After the 2h window, a sweeper/lazy check disables the user.
- [ ] All Mongo docs, PVC files, Chroma embeddings, and Redis sessions owned by the temp user are removed.
- [ ] Shared resources created by the temp user are also removed (option 2).
- [ ] Purge is idempotent and safe to re-run.
- [ ] Unit tests cover the purge for each resource type and idempotency.