# Ticket: PAIML-POLA-API-017

## Title
[Application] Rewire `main.py` (drop Postgres/InMemory) + remove chatbot `analyze` tool

## Description
Phase 11 (§8.3.4 bullets 4-5). Update app assembly so `ToolsService` is constructed without Postgres /
InMemory reference+attempt repos, and remove the chatbot `analyze` tool + `_analyze_handler` (its whole
dependency chain is deleted), while keeping the `histogram` tool calling the processor directly.

## What to Do (Implementation Steps)
- [ ] Step 1: `main.py::_build_tools_service` — drop `DATABASE_URL`/Postgres + InMemory reference/attempt construction.
- [ ] Step 2: Construct `ToolsService` without reference/attempt repos.
- [ ] Step 3: Remove the `analyze` tool registration and `_analyze_handler`.
- [ ] Step 4: Keep `histogram` tool → `tools_service.histogram(...)` (processor, not the HTTP endpoints).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] App starts without Postgres wiring; no reference/attempt deps.
- [ ] Chatbot `analyze` tool is gone; `histogram` tool still works.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` startup + chatbot tool registry tests (see PAIML-POLA-API-018).

## Dependencies
- **Blocks**: PAIML-POLA-API-018, PAIML-POLA-API-019
- **Blocked By**: PAIML-POLA-API-009, PAIML-POLA-API-016

## Estimated Effort
- [M]
