# Ticket: PAIML-POLE-RAG-031

## Title
[CI] Include pole_rag sources in base-image content hash

## Description
Phase 6 follow-up (predicted in 027 review, confirmed by 028). The
`.github/workflows/build-push.yml` `HASH_INPUTS` in `pole-ai-ml` hashes
`base.Dockerfile` + 7 pyprojects + the model file, but NOT
`packages/pole_rag/**` (`pole_rag` has no pyproject by design, Phase 1).
Ticket 028 changed only `packages/pole_rag/src/pole_rag/config.py` →
identical base hash → CI reused the stale base → current `:develop` image
ships `pole_rag` files WITHOUT the `POLE_RAG_DATA_DIR` override. Seeding
`/data/rag` now would sit unread.

Note: merging this ticket triggers the slow base-rebuild lane once (~10+ min).
Ticket 030's staging verification needs the rebuilt image + a staging restart.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Step 1 [pole-ai-ml]: In `.github/workflows/build-push.yml`, add the
      `pole_rag` source tree to `HASH_INPUTS` (e.g. a stable
      `find packages/pole_rag/src -type f | sort | sha256sum` line or an
      explicit file list — developer picks the exact form; constraint:
      deterministic under re-runs, no timestamps), so any `pole_rag` change
      forces a base rebuild.
- [ ] Step 2 [pole-ai-ml]: Prove the tag moves: run the hash snippet on
      identical `develop` HEAD before/after the edit and paste both tags in
      the ticket/PR body.
- [ ] Step 3 [pole-ai-ml]: Confirm no other workflow behaviour changed
      (`git diff` shows only the `HASH_INPUTS` line(s)); `helm`/app code
      untouched.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `HASH_INPUTS` references `pole_rag` sources.
- [ ] Proof the computed tag changes vs the pre-fix hash on identical
      `develop` HEAD (both tags pasted).
- [ ] No other workflow behaviour changed.
- [ ] `helm`/app code untouched.
- [ ] The changes do not break existing unit tests (regression check —
      workflow-only change).

## Integration Tests to Run (Local Verification)
- [ ] Hash snippet before → tag A; after → tag B; A ≠ B on the same HEAD.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-030
- **Blocked By**: —

## Estimated Effort
- [S]
