# Ticket: PAIML-KEYCLOAK-008

## Title
[pole_api] Owner-scoped audit of temp-user resources

## Description
Audit that every resource a temp user can create persists `owner_id` (the Keycloak `sub`), so the purge can enumerate exactly what to delete. Resources include videos, clips, uploads, analysis videos/histograms/landmarks, athlete profile, crawler posts/images, training classes, model runs, and chatbot sessions. Backfill `owner_id` on write for temp users where missing.

## What to Do (Implementation Steps)
- [ ] Audit repositories for `owner_id` persistence: video, clip, upload, analysis (video/histogram/landmarks), profile, crawler (post/image/crawl), training (class/model run), chatbot session
- [ ] Identify any write path that a temp user could hit without recording `owner_id`
- [ ] Backfill `owner_id` on write for temp users so every created resource is attributable

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Every temp-user-created resource is attributable to the Keycloak `sub`
- [ ] Documented inventory of resources + their collections/PVC paths for the purge

## Integration Tests to Run (Local Verification)
- [ ] As a temp user, create one of each resource; confirm `owner_id` is set on all of them

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-009
- **Blocked By:** PAIML-KEYCLOAK-002

## Estimated Effort
- [L] (Large 2–4h)