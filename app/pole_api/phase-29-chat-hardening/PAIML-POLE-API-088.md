# Ticket: PAIML-POLE-API-088

## Title
[Chatbot] Backend never echoes raw JSON for unknown block types

## Description
Phase 29 (follow-up hardening from the phase-28 QA gate). `app/pole_api/src/analyst_chatbot/blocks.py` `parse_blocks()` drops unknown block types, but has no all-unknown fallback: when an LLM reply parses to JSON yet contains ZERO valid block types (only unknown types like the legacy `metric_deviation` removed from the prompt contract in API-085), the unknown items are dropped and the raw JSON array string leaks back out md-wrapped as `content` — the exact symptom API-087 was meant to kill. Same gap applies to `normalize_reply_text()` / `blocks_to_text()`: the wire `reply` must never be a JSON array string.

**Fix:** when a reply parses to JSON but yields zero valid blocks, drop the unknown blocks and return a plain "no usable content" markdown block instead of md-wrapping the raw JSON array string. Keep the FE-friendly contract: valid mixed replies still drop unknown items silently.

## What to Do (Implementation Steps)
- [ ] In `parse_blocks()` (`app/pole_api/src/analyst_chatbot/blocks.py`): detect the parses-to-JSON-but-zero-valid-blocks case and return a single plain "no usable content" markdown block instead of md-wrapping the raw JSON array string.
- [ ] Extend the same guarantee to `normalize_reply_text()` / `blocks_to_text()`: the wire `reply` must never be a JSON array string.
- [ ] Keep the FE-friendly contract: valid mixed replies (some valid + some unknown items) still drop the unknown items silently, unchanged.
- [ ] Add parametrized `parse_blocks` / `normalize_reply_text` tests covering all-unknown, mixed, malformed, and empty inputs; assert no raw JSON appears in any md `content`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] All-unknown LLM block payloads yield a plain "no usable content" markdown block, never md-wrapped raw JSON.
- [ ] No raw JSON in any md `content`; wire `reply` is never a JSON array string.
- [ ] Mixed valid replies unchanged (unknown items dropped silently).
- [ ] Parametrized tests (all-unknown, mixed, malformed, empty) added and green.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: —
- **Blocked By**: — (does NOT block API-089; independent — either may land first)

## Estimated Effort
- [S]
