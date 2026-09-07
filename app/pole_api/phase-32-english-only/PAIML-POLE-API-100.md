# Ticket: PAIML-POLE-API-100

## Title
[Chatbot] Analyst + training replies always in English (drop mirror-language)

## Description
Phase 32 — staging Chrome test (095 acceptance) showed both analyst answers
in Spanish despite English questions ("What videos do I have?" →
"📹 Tus videos disponibles…"). Root cause: both chatbot system prompts say
"You may answer in Spanish or English; mirror the user's language", and
with Spanish-heavy RAG context the model defaults to Spanish even for
English input. Product decision: answers are always in English.

Fix (implemented in `feature/PAIML-POLE-API-100-english-only`):
- `app/pole_api/src/analyst_chatbot/prompts.py`: mirror clause →
  English-always directive.
- `app/pole_api/src/training_chatbot/prompts.py`: same change (same
  pattern, same failure mode).

## What to Do (Implementation Steps)
- [x] Replace mirror-language clause with English-always in both prompts.
- [x] Confirm no test pins the old wording; run analyst/training chatbot
      prompt suites.
- [ ] Deploy to staging; re-ask in English; assert English reply.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] Prompt suites green.
- [ ] Staging: English question → English answer (Chrome check).

## Integration Tests to Run (Local Verification)
- [x] `test_analyst_chatbot.py`, `test_training_chatbot.py` (prompt/wiring)

## Dependencies
- **Blocks**: None.
- **Blocked By**: None.

## Estimated Effort
- [XS]
