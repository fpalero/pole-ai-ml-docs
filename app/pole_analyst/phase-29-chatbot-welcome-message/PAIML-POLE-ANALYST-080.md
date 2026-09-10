# Ticket: PAIML-POLE-ANALYST-080

## Title
[Chatbot] Welcome message with capabilities overview and clickable quick-reply pills

## Description
**Phase 29: Chatbot Welcome Experience**

When a user accesses the chatbot for the first time after login, the chat is empty. Add a default welcome message that explains what the chatbot can do, with example questions as clickable quick-reply pills.

### Requirements

1. **Frontend Welcome Message**
   - Update `WELCOME_MESSAGE` in `chat-message.ts` to show a rich welcome message
   - Message should explain the chatbot's capabilities (4-6 main features)
   - Include clickable quick-reply pills for example questions
   - Show the message always on first page load (regardless of library state)

2. **Backend Tool: `get_capabilities`**
   - Create a new tool `get_capabilities` in `analyst_chatbot/tools.py`
   - **Empty parameters:** Return all capabilities with explanations and 2 examples each
   - **With capability name (e.g., `get_capabilities("analysis")`):** Return a step-by-step tutorial

3. **Capabilities to include:**
   - Video Analysis - Upload and analyze videos
   - Progress Tracking - Compare sessions over time
   - Technique Feedback - Get detailed form corrections
   - Injury Prevention - Risk scanning and safety tips
   - Training Plans - Personalized improvement plans
   - Cohort Comparison - See how you rank vs others

### Technical Details

**Frontend Changes:**
- `app/pole_analyst/src/app/features/chat/models/chat-message.ts`: Update `WELCOME_MESSAGE`
- `app/pole_analyst/src/app/features/chat/components/chat-pane/chat-pane.component.ts`: Remove `isEmptyLibrary` condition

**Backend Changes:**
- `app/pole_api/src/analyst_chatbot/tools.py`: Add `GET_CAPABILITIES` tool
- `app/pole_api/src/analyst_chatbot/facade.py`: Add `get_capabilities()` method

### Acceptance Criteria

1. ✅ Welcome message shows on first page load
2. ✅ Message explains 4-6 capabilities with brief descriptions
3. ✅ Quick-reply pills are clickable and send the example question
4. ✅ Backend tool `get_capabilities()` returns capabilities list
5. ✅ Backend tool `get_capabilities("analysis")` returns tutorial
6. ✅ Unit tests pass for both frontend and backend
7. ✅ E2E test verifies welcome message appears

## Blocks
- None

## Blocked By
- None

## Phase
Phase 29: Chatbot Welcome Experience

## Status
📋 PLANNED

## Assignee
Developer

## Estimated Effort
Medium (2-3 hours)

## Files Affected
- `app/pole_analyst/src/app/features/chat/models/chat-message.ts`
- `app/pole_analyst/src/app/features/chat/components/chat-pane/chat-pane.component.ts`
- `app/pole_api/src/analyst_chatbot/tools.py`
- `app/pole_api/src/analyst_chatbot/facade.py`
- `app/pole_analyst/src/app/features/chat/models/chat-message.spec.ts`
- `app/pole_api/tests/test_analyst_chatbot.py`
