# PAIML-POLE-ANALYST-038 — DTOs for enriched analysis summary list

## Meta
- **Project:** pole_analyst
- **Phase:** 12 — Stitch Design: Tab Navigation + Analysis History
- **Status:** TODO
- **Blocks:** PAIML-POLE-ANALYST-041
- **Blocked By:** — (none)

## Description

Create the TypeScript DTO models for the enriched analysis summary list endpoint
(`GET /api/analysis/videos/summary`). The current `VideoRecord` interface in
`core/models/api.models.ts` does not include `trick_label`, `overall_score`, or `phases`.

### New interfaces

```typescript
/** Enriched video record with analysis summary data (from /api/analysis/videos/summary). */
export interface AnalysisSummaryRecord {
  _id: string;
  filename: string;
  analyzed: boolean;
  trick_label: string | null;
  overall_score: number | null;
  phases: {
    init: { start: number; end: number };
    execution: { start: number; end: number };
    exit: { start: number; end: number };
  } | null;
  created_at: string; // ISO date
}
```

### Tasks
- [ ] Add `AnalysisSummaryRecord` interface to `core/models/api.models.ts`.
- [ ] Add unit tests for the interface (type-checking only, pure model).
- [ ] Ensure the interface matches the backend response shape from PAIML-POLE-API-056.

### Acceptance Criteria
- [ ] `AnalysisSummaryRecord` interface exists and matches the backend contract.
- [ ] Unit tests pass.
