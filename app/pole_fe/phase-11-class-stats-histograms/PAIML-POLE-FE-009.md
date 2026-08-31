# Ticket: PAIML-POLE-FE-009

## Title
[Domain/App] DTOs + servicios (`ReferenceHistogramDto`; `generateReferences`, `getClassHistogramStats`)

## Description
Phase 11 (§1). Domain/App layer for reference histograms in `pole_fe`: DTOs and services to generate
reference histograms for a trick and read class histogram stats, consuming the backend
`pola_api` reference endpoints.

## What to Do (Implementation Steps)
- [ ] `ReferenceHistogramDto` (metric, phase, bins, counts, total, source_count, last_updated).
- [ ] `generateReferences(trick_label, videoIds)` → POST `/api/tools/histograms/references` → 202 `{job_id}`.
- [ ] `getClassHistogramStats(trick_label)` → GET `/api/tools/histograms/references?trick_label=` → list of metrics (handles 422 empty).
- [ ] `getReferenceClasses()` → GET `/api/tools/histograms/classes`.
- [ ] Unit tests for services (mock HTTP).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Services consume the reference endpoints with correct DTO mapping.
- [ ] 422 empty reference mapped to empty-state DTO with `missing_metrics`.
- [ ] `npx ng test --watch=false` green on new modules.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`.

## Dependencies
- **Blocks**: PAIML-POLE-FE-010, PAIML-POLE-FE-011
- **Blocked By**: PAIML-POLE-API-044

## Estimated Effort
- [M]