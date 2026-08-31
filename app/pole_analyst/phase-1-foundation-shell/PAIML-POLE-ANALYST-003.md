# Ticket: PAIML-POLE-ANALYST-003

## Title
[Presentation] Shared UI atoms (StatusChip, TabBar, Card, Badge, UploadDropzone)

## Description
Build the reusable shared UI atoms used across the app, matching the Stitch design:
`StatusChip` (Idle/Thinking/Working/Completed/Error), `TabBar`, `Card`, `Badge`
("Analyzed"/"Not analyzed"), and `UploadDropzone` (drag & drop + file input).

## What to Do (Implementation Steps)
- [ ] Implement `StatusChip` with dot + label + spinner variants driven by `ChatState`.
- [ ] Implement `TabBar` with active/inactive states (accent underline).
- [ ] Implement `Card`, `Badge` (semantic colors: green/amber/red/gray).
- [ ] Implement `UploadDropzone` (drag & drop, `.mp4` accept, size/format hooks).
- [ ] Ensure WCAG 2.1 AA (contrast, labels, focus states).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] Each atom renders all its states and is keyboard-accessible.

## Integration Tests to Run (Local Verification)
- [ ] UC-03: tab bar switches tabs; UC-01/UC-05: upload dropzone accepts/rejects files.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-005, PAIML-POLE-ANALYST-008, PAIML-POLE-ANALYST-012, PAIML-POLE-ANALYST-016, PAIML-POLE-ANALYST-017, PAIML-POLE-ANALYST-018, PAIML-POLE-ANALYST-019
- **Blocked By**: PAIML-POLE-ANALYST-001

## Estimated Effort
- [M]
