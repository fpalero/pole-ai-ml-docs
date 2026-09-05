# Ticket: PAIML-POLE-RAG-030

## Title
[Application] Verify RAG tools on staging (hits + unknown-DB `ToolError`)

## Description
Phase 6, step 4 of 4 (verification, no repo file changes expected). Prove the
shipped image + wired data dir + seeded DBs answer on staging, and that the
safe missing-DB contract still holds. If this ticket goes red, re-open against
027/028/029 in order — do not patch around it here.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Step 1 [pole-ai-ml]: From staging (port-forward or debug pod with the
      rolled image), run per tool with `data_dir=/data/rag`:
      `query_pole`, `query_calisthenics`, `query_psicology`,
      `query_biomechanics` each with a domain probe (e.g. pole → "invert grip
      technique"; calisthenics → "muscle-up progression"; psicology → "mindful
      athlete focus"; biomechanics → "shoulder torque") and `k=3`.
- [ ] Step 2 [pole-ai-ml]: Assert per tool: exactly `k` results, merged across
      `text_chunks` + `image_descriptions` sorted by distance ascending, each
      carrying `source_document` (+ `image_path` for image captions).
- [ ] Step 3 [pole-ai-ml]: Assert the safe-unknown contract: query a
      nonexistent DB name (e.g. `--name unknown_db_xyz`) → `FileNotFoundError`
      surfaced as `ToolError`, no pod crash/restart (`kubectl get pods`
      restart count unchanged).
- [ ] Step 4 [pole-ai-ml]: Assert `/data/chroma` untouched: movement-store
      count query still returns 7712 entries (or current baseline recorded in
      029); video similarity flow smoke still green.
- [ ] Step 5 [pole-ai-ml]: Record evidence on the release ticket (per-tool
      output excerpts, pod image digest, `/data/rag` listing, restart counts).
      No repo files change in this ticket unless a regression fix is split out
      as a new ticket (do not bundle fixes here).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] All 4 tools return k=3 hits with metadata on staging against
      `/data/rag`.
- [ ] Unknown DB → `ToolError` (no crash).
- [ ] `/data/chroma` movement store intact; video flow unaffected.
- [ ] Evidence attached to the release ticket; Phase 6 flippable to DONE.
- [ ] The changes do not break existing unit tests (regression check —
      nothing to merge, verification only).

## Integration Tests to Run (Local Verification)
- [ ] UC-05/UC-07 staging analogues: seeded staging DB → tools return expected
      sources; unknown DB → graceful `ToolError`.

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLE-RAG-029, PAIML-POLE-RAG-035, PAIML-POLE-RAG-036

## Estimated Effort
- [S]
