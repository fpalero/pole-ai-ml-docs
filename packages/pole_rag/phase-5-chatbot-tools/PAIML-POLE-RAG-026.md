# Ticket: PAIML-POLE-RAG-026

## Title
[Application] Integration test: chatbot tools query a seeded temp DB

## Description
Phase 5: live integration test (marked `integration`) that seeds a temp DB and calls the
4 tool handlers, asserting results reference expected source documents. Confirms the
full rag→chatbot path.

## What to Do (Implementation Steps)
- [ ] Step 1: Create `packages/chatbot/tests/test_rag_tools_live.py` marked `integration`.
- [ ] Step 2: Seed a temp DB via `seed_resource` with the smallest source PDF (skip if no
      sources present), or reuse a prebuilt tiny fixture.
- [ ] Step 3: Invoke each handler (`query_pole`, `query_calisthenics`, `query_psicology`,
      `query_biomechanics`) with `data_dir=tmp`.
- [ ] Step 4: Assert the corresponding tool returns results whose `source_document`
      matches the seeded PDF (for the matching resource; others may return empty —
      assert graceful behavior).
- [ ] Step 5: Run via `pixi run test-chatbot-live`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Integration test passes locally with real services.
- [ ] Tools behave gracefully on empty/unknown DBs.
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-07 end-to-end: seeded temp DB → tools return expected sources.

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLE-RAG-016, PAIML-POLE-RAG-024

## Estimated Effort
- [M]