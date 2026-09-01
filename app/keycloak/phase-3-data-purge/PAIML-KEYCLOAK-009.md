# Ticket: PAIML-KEYCLOAK-009

## Title
[pole_api] Expiry purge: delete all temp-user data + disable user

## Description
Implement `TempAccessPurgeService` keyed by the temp user's `owner_id`. On expiry, delete **every** resource the temp user created — including shared/global ones (option 2; temp users must not leave data that could corrupt the app) — reuse existing deletion services, remove physical files on the PVC, clear Redis chatbot sessions + `temp:*` keys, then disable the Keycloak user (kept for audit).

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] `core/temp_access.py` — `TempAccessPurgeService(owner_id)`: enumerate owned resources and delete via existing services (`VideoDeletionService`, `AnalysisService.delete_video`, crawler post/image deletion, profile delete, class cascade, chroma/window deletion)
- [ ] Delete physical files on PVC (uploads, analysis_uploads, curated, downloads, chroma) referenced by owned resources
- [ ] Delete Redis chatbot sessions + clear `temp:*` keys for the email
- [ ] Disable the Keycloak user via the admin client (kept for audit)
- [ ] Option 2: also delete shared/global resources the temp user created (classes, curated clips, model runs)
- [ ] Make the purge idempotent (already-deleted files/docs skipped)

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] All Mongo docs, PVC files, Chroma embeddings, and Redis sessions owned by the temp user removed
- [ ] Shared resources created by the temp user also removed (option 2)
- [ ] Keycloak user disabled; `temp:*` keys cleared
- [ ] Purge is idempotent and safe to re-run

## Integration Tests to Run (Local Verification)
- [ ] Create resources as a temp user, run the purge, confirm everything is gone and the user is disabled

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-010
- **Blocked By:** PAIML-KEYCLOAK-005, PAIML-KEYCLOAK-008

## Estimated Effort
- [L] (Large 2–4h)