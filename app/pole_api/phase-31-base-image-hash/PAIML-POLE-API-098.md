# Ticket: PAIML-POLE-API-098

## Title
[CI] Base-image content hash misses local package sources — staging shipped new app code against stale `pole_chatbot`

## Description
Phase 31 — follow-up to PAIML-POLE-API-095.

Staging evidence (pod `pole-ai-pole-api-855b4cc54c-xl226`, rolled out 04:19Z
after infra#31): all three chatbot slices skipped at startup —
`PoleLangGraphAgent.__init__() got an unexpected keyword argument
'max_turn_seconds'`. Inside the pod, `/app/main.py` has the 095 code while
the pip-installed `pole-chatbot 0.1.0` in `/opt/venv` predates it (zero
matches for `max_turn_seconds`/`TURN_TIMEOUT`). Every chat turn currently
gets the 503 unavailable fallback instead of answers.

Root cause: `.github/workflows/build-push.yml` (`base` job) tags the heavy
`pole-api-base` image from a content hash covering only `base.Dockerfile`,
the packages' `pyproject.toml` files, the landmark `.task`, and the
`pole_rag` source tree (PAIML-POLE-RAG-031). The base image pip-installs
SEVEN local packages (`pole-crawler`, `pole-train-model`, `pole-crop`,
`jobs`, `chatbot`, `pole-tools`, `analysis-tools`), but none of their
`src/` trees is hashed. The 095 change touched only
`packages/chatbot/src/*.py` → identical base tag → the base build was
skipped (finished in 3s) → thin app image built over a stale base.

Fix (implemented in `feature/PAIML-POLE-API-098-base-hash`):
- Hash tracked sources (`git ls-files`) of all seven pip-installed packages
  plus `pole_rag` (replacing the RAG-031 explicit `find`, same semantics on
  a fresh CI checkout, immune to local `__pycache__`/`venv` noise) into the
  base tag. Any src-only package change now forces a base rebuild.

## What to Do (Implementation Steps)
- [x] Extend `Compute base content hash` step: `PKG_SRC_HASH` over tracked
      sources of all locally-built packages; fold into `TAG`.
- [x] Verify locally: new tag differs from old tag on current tree (bust
      proven); workflow YAML still parses.
- [ ] Merge → rebuild produces a fresh base → app image consistent →
      redeploy staging → verify slices wire (`analyst chatbot slice wired…
      model=deepseek/deepseek-v4-flash`, no `skipped` lines).
- [ ] Rerun staging WS chat battery (2-question Chrome smoke at minimum).

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] `TAG` changes when any file under a pip-installed package's tracked
      sources changes; unchanged otherwise (no gratuitous ~10 min rebuilds).
- [ ] Staging pod starts with all chatbot slices wired (no `slice skipped`
      lines) after the post-merge rebuild + redeploy.
- [ ] Chatbot answers on staging (deepseek model) — Chrome 2-question test.

## Integration Tests to Run (Local Verification)
- [x] Local tag-bust check (old vs new computation on the worktree).
- [ ] Post-merge: `Build & Push to GHCR` green on develop; `Deploy to DEV`
      green; pod startup log shows wired slices.

## Dependencies
- **Blocks**: Staging Chrome 2-question validation (095 acceptance item).
- **Blocked By**: None.

## Estimated Effort
- [S]
