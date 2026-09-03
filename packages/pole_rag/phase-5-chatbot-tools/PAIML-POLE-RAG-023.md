# Ticket: PAIML-POLE-RAG-023

## Title
[Application] Make `pole_rag` importable from the chatbot (workspace PYTHONPATH)

## Description
Phase 5: because `pole_rag` has **no standalone pyproject / editable install**, the chatbot
cannot depend on `pole-rag` as a pip package. Instead, the chatbot runtime must include
`packages/pole_rag/src` on its `PYTHONPATH` so the 4 query tools can `import pole_rag`. No
tool logic yet.

## What to Do (Implementation Steps)
- [ ] Step 1: Identify how the chatbot is run (e.g., `pixi run chatbot-api`,
      `test-chatbot`, or the `pola_api` consolidation) and add
      `packages/pole_rag/src` to its `PYTHONPATH` (task env or launcher).
- [ ] Step 2: Verify `import pole_rag` works from the chatbot's context.
- [ ] Step 3: Confirm import discipline: chatbot may only import `pole_rag` public API.
- [ ] Step 4: Do NOT add `pole-rag` to any `pyproject.toml` (chatbot or rag).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pole_rag` importable from the chatbot runtime via PYTHONPATH.
- [ ] No `pole-rag` pip dependency added anywhere.
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-07 prerequisite: tools import path resolves.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-024
- **Blocked By**: PAIML-POLE-RAG-002

## Estimated Effort
- [S]