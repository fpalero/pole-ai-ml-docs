# Ticket: PAIML-POLE-ANALYST-083

## Title
[Chatbot] Welcome message expansion to the full capability catalog

## Description
**Phase 33: Welcome Message Expansion**

The WELCOME_MESSAGE lists only the 6 original capabilities. Expand it to the 10-capability catalog (the FE sister of PAIML-POLE-ANALYST-082). Capability titles MUST match the CAPABILITIES titles defined in the BE catalog (ticket 082): Video Analysis, Progress Tracking, Technique Feedback, Injury Prevention, Training Plans, Cohort Comparison, Trick Teaching, Sport Psychology, Corrective Exercises, Video Editing.

### Requirements

1. Update WELCOME_MESSAGE in `app/pole_analyst/src/app/features/chat/models/chat-message.ts` so the md block lists exactly the 10 capabilities above with emoji + one-line description (keep the existing 6 verbatim, append the new 4: 7. 📚 Trick Teaching — explain any trick: technique, key phases, muscles, common mistakes. 8. 🧠 Sport Psychology — motivation, dealing with fear, focus and mental prep. 9. 💪 Corrective Exercises — drills and calisthenics for the errors I flag. 10. ✂️ Video Editing — crop a segment or extract single frames from a video.). End with "_Tap a suggestion below, or just ask \"what can you do?\" anytime!_".
2. Update the plain-text `reply` field to mirror the md list (10 capabilities) so notification/accessibility text stays in sync.
3. Update the quick_replies block to the user-approved pill set (7 pills): 'Analyze my latest video', 'Am I improving?', 'Teach me the ayesha', 'How do I stay motivated?', 'Am I at injury risk?', 'Build my 4-week plan', 'What should I work on next?'.
4. Update `app/pole_analyst/src/app/features/chat/models/chat-message.spec.ts` WELCOME_MESSAGE tests to assert: role assistant, no toolCalls, md block contains all 10 capability titles, quick_replies block has the 7 pills, and reply string contains 'Video Editing'.

### Technical Details

- `app/pole_analyst/src/app/features/chat/models/chat-message.ts`
- `app/pole_analyst/src/app/features/chat/models/chat-message.spec.ts`

### Acceptance Criteria

1. Welcome md block lists exactly 10 capabilities.
2. quick_replies has exactly the 7 approved pills.
3. reply string mirrors the md list (contains 'Video Editing').
4. chat-message.spec.ts updated and FE unit tests + lint green (npm test in app/pole_analyst; also `npm run lint` if the FE lint target exists).
5. No other FE component behavior changes (chat-pane welcome display unaffected).

## Blocks
- None

## Blocked By
- None (FE text only; BE catalog naming contract is followed manually — titles must match 082's CAPABILITIES titles)

## Phase
Phase 33: Capability Catalog Expansion

## Status
📋 PLANNED

## Assignee
fe-developer

## Estimated Effort
Small (1 hour)

## Files Affected
- `app/pole_analyst/src/app/features/chat/models/chat-message.ts`
- `app/pole_analyst/src/app/features/chat/models/chat-message.spec.ts`
