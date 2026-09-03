# Ticket: PAIML-KEYCLOAK-014

## Title
[Infrastructure] Stitch pixel-perfect login restyle (`pole-ai-login` theme)

## Description
Restyle the `pole-ai-login` Keycloak login theme pixel-perfect to the Stitch
design (desktop + mobile), keeping the temp-access POST behavior intact.

<!-- Cross-repo note: primary delivery is the infra repo (theme + chart);
     this file is the docs-repo merge record. No prior ticket body existed;
     reconstructed from the team-lead handover — scope states only those facts. -->
## Repository
pole-ai-ml-infra (delivery) / pole-ai-ml-docs (this record)

## What to Do (Implementation Steps)
- [x] Restyle `pole-ai-login` theme to the Stitch design (desktop + mobile)
- [x] fe-developer conformance check → PIXEL-PERFECT, no fix PR
- [x] Tester phase-end QA gate (local k3s rev 13) → GREEN, 4/4

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] Theme matches the Stitch design (fe-developer PIXEL-PERFECT)
- [x] Phase-end QA gate GREEN (4/4, error list empty)
- [ ] USER manual testing + manual develop→main promotion (open — ticket NOT
      closed until the user confirms)

## Merge record
- Infra PR [#24](https://github.com/fpalero/pole-ai-ml-infra/pull/24) —
  MERGED (squash `b04bb69` into `develop`)

## QA gate (summary; full detail in `plan/PLAN_PHASE_6.md`)
- Visual desktop+mobile; password POST failure-path; magic-link 202/Mailpit +
  422 + 409; en render + es key parity. Evidence: `/tmp/qa014-*`.
- Non-blocking: (1) realm i18n flag off locally (es fallback, theme parity
  proven); (2) relative `/api/auth/temporary-access` fetch with
  `data-endpoint` override (pre-existing Phase 2 behavior).

## Integration Tests to Run (Local Verification)
- [ ] N/A (merge record; QA evidence in `/tmp/qa014-*`)

## Dependencies
- **Blocks:** None
- **Blocked By:** PAIML-KEYCLOAK-003 (custom login theme)

## Estimated Effort
- [M] (Medium < 1 day)
