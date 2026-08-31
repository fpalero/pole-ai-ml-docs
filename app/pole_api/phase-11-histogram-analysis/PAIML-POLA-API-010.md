# Ticket: PAIML-POLA-API-010

## Title
[Infrastructure] Add `_describe_done` histogram branch in `core/jobs.py`

## Description
Phase 11 (§8.3.2 bullet 4). Add a `_describe_done` branch so the histogram-analysis job's success
description surfaces per-video errors ("Processed N, Skipped M, Failed K — …") instead of a generic
message.

## What to Do (Implementation Steps)
- [ ] Step 1: In `app/pola_api/src/core/jobs.py`, add a branch keyed on the histogram-analysis result shape (`processed/skipped/failed/histograms`).
- [ ] Step 2: Build a human-readable description including per-video failure reasons.
- [ ] Step 3: Ensure existing job descriptions for other kinds are unchanged.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] A `done` histogram-analysis job's description lists processed/skipped/failed counts and reasons.
- [ ] No regression on other job `_describe_done` branches.

## Integration Tests to Run (Local Verification)
- [ ] UC-94 — assert the description surfaces the per-video error.

## Dependencies
- **Blocks**: PAIML-POLA-API-008
- **Blocked By**: —

## Estimated Effort
- [S]
