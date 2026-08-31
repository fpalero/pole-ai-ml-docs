# Ticket: PAIML-POLE-ANALYST-021

## Title
[Presentation] Invalid upload error handling

## Description
Handle invalid uploads (non-`.mp4`, oversized file) with an inline error and guidance to choose
another or a shorter video. Map backend `422` (or client-side validation) into a user-friendly
message.

## What to Do (Implementation Steps)
- [ ] Add client-side validation in `UploadDropzone` (extension, size).
- [ ] Surface `422 {detail}` from the upload as an inline error.
- [ ] Render guidance ("choose another video" / "shorter video").

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] Invalid files are blocked inline with actionable guidance.

## Integration Tests to Run (Local Verification)
- [ ] UC-05: non-`.mp4`/oversized file shows an inline error and no upload occurs.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-024
- **Blocked By**: PAIML-POLE-ANALYST-011, PAIML-POLE-ANALYST-012

## Estimated Effort
- [S]
