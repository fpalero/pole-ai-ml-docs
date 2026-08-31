# Ticket: PAIML-POLE-ANALYST-027

## Title
[Application] QA checklist + accessibility pass

## Description
Final QA pass: verify all endpoints are wired, every component handles
empty/loading/error/success, keyboard navigation works, `aria-live` announces job/chat state
changes, and WCAG 2.1 AA is met.

## What to Do (Implementation Steps)
- [ ] Verify each FE service hits its backend endpoint (upload/list/analyze/summary/histogram/pose).
- [ ] Verify each component's empty/loading/error/success states.
- [ ] Verify keyboard nav + `aria-live` for the status chip and toasts.
- [ ] Run an accessibility spot audit (WCAG 2.1 AA).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] QA checklist items all pass; accessibility issues resolved or logged.

## Integration Tests to Run (Local Verification)
- [ ] UC-01..07 manual walkthrough + keyboard/AT spot checks.

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLE-ANALYST-026

## Estimated Effort
- [M]
