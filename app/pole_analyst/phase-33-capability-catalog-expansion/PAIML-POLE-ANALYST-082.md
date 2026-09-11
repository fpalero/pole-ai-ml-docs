# Ticket: PAIML-POLE-ANALYST-082

## Title
[Chatbot] Capability catalog expansion + synonym/keyword routing + prompt wiring

## Description
**Phase 33: Capability Catalog Expansion**

The chatbot currently advertises 6 capabilities but its real tool surface (~23 tools incl. 4 RAG knowledge bases) supports more. User reported that "How could you prevent injuries?" returned the graph-level safe fallback instead of the injury_prevention tutorial. Root cause: get_capabilities is absent from the analyst system prompt, CAPABILITY_ALIASES lacks "prevent/prevention/injuries", and the catalog doesn't advertise the real capabilities (trick teaching, sport psychology, corrective exercises, video editing). This ticket expands the catalog + resolution + prompt routing (BE). Sister ticket PAIML-POLE-ANALYST-083 covers the FE welcome message text.

### Requirements

1. Expand CAPABILITIES in `app/pole_api/src/analyst_chatbot/facade.py` from 6 to 10 entries, keeping the existing 6 (analysis, progress, technique, injury_prevention, training_plan, cohort) unchanged and ADDING 4 new canonical keys:
   - "trick_teaching" — title "Trick Teaching", description "Explain any trick: technique, key phases, muscles, common mistakes.", 2 example questions (e.g. "Teach me the ayesha", "How do I learn a handspring?"), step-by-step tutorial.
   - "sports_psychology" — title "Sport Psychology", description "Motivation, dealing with fear, focus and mental preparation.", 2 examples (e.g. "How do I stay motivated?", "I'm scared of the ayesha, help"), tutorial.
   - "corrective_exercises" — title "Corrective Exercises", description "Drills and calisthenics for the errors I flag.", 2 examples (e.g. "Which exercises fix my hip drop?", "Give me drills for my wrist stability"), tutorial.
   - "video_editing" — title "Video Editing", description "Crop a segment or extract single frames from a video.", 2 examples (e.g. "Crop my last video from 2s to 6s", "Extract frame 120"), tutorial.
   All entries keep the {title, description, examples[2], tutorial[]} shape. Update the module docstring/comment that says "six" to "ten".
2. Expand CAPABILITY_ALIASES in `facade.py` to cover the new entries AND close the reported gap. At minimum add: "prevent", "prevention", "prevent injuries", "injuries", "avoid injuries", "stay safe" → injury_prevention; "teach", "teach me", "explain", "learn", "tutorial" → trick_teaching; "motivation", "psychology", "mental", "fear", "mindset", "confidence" → sports_psychology; "exercises", "drills", "corrective exercises", "calisthenics" → corrective_exercises; "crop", "edit", "extract frames", "cut", "frames" → video_editing.
3. Add a CAPABILITY_KEYWORDS dict (prefix-stem keyword sets per canonical key) + a small deterministic matcher `_match_capability_keywords(raw: str) -> str | None` used as a FALLBACK in get_capabilities after the exact alias lookup misses: normalize (lowercase, "-"→" ", "_"→" "), split into tokens, stem each token by first 6 chars, hit key if any token (or its stem) is in the key's keyword set. Resolution order in get_capabilities: (1) exact alias key, (2) normalized alias key, (3) keyword matcher, (4) structured {"error", "valid_capabilities"} response — never raises. Keyword sets MUST include "injur", "prevent", "safety", "safe", "risk" for injury_prevention so "prevent injuries"/"injuries" resolve via stem.
4. Update `app/pole_api/src/analyst_chatbot/prompts.py` ANALYST_SYSTEM_PROMPT: (a) add get_capabilities to the enumerated tool list ("- get_capabilities: describe capabilities and return step-by-step tutorials for one capability."), and (b) add a CAPABILITY-ROUTING RULE (MANDATORY) stating: when the user asks what the chatbot can do, for help, or a how-to on a capability ("how do I prevent injuries?", "teach me X", "help with motivation", "what can you do?") call get_capabilities FIRST (omit the selector for the full catalog; pass a canonical selector or synonym for one capability) and render the returned tutorial/examples — never answer capability questions from memory or the safe fallback.
5. Update the GET_CAPABILITIES tool description in `app/pole_api/src/analyst_chatbot/tools.py` to say the catalog has ten capabilities and list all canonical selectors.

### Technical Details

- `app/pole_api/src/analyst_chatbot/facade.py` — CAPABILITIES, CAPABILITY_ALIASES, new CAPABILITY_KEYWORDS + matcher, get_capabilities() resolution chain.
- `app/pole_api/src/analyst_chatbot/prompts.py` — ANALYST_SYSTEM_PROMPT tool list + CAPABILITY-ROUTING RULE.
- `app/pole_api/src/analyst_chatbot/tools.py` — GET_CAPABILITIES description.
- Tests: `app/pole_api/tests/test_analyst_capabilities_tool.py` (or existing capability test module — find it and extend).

### Acceptance Criteria

1. get_capabilities() with no args returns all 10 capabilities.
2. get_capabilities("prevent injuries") and get_capabilities("injuries") return the injury_prevention tutorial (via keyword/stem fallback).
3. get_capabilities("motivation") returns sports_psychology; get_capabilities("teach me") returns trick_teaching.
4. get_capabilities("nonsense") returns the structured error with valid selectors; no exception.
5. ANALYST_SYSTEM_PROMPT includes get_capabilities and the CAPABILITY-ROUTING RULE.
6. All BE unit tests pass (pytest for app/pole_api tests; coverage ≥ 80%).

## Blocks
- None

## Blocked By
- None

## Phase
Phase 33: Capability Catalog Expansion

## Status
📋 PLANNED

## Assignee
Developer

## Estimated Effort
Medium (2-3 hours)

## Files Affected
- `app/pole_api/src/analyst_chatbot/facade.py`
- `app/pole_api/src/analyst_chatbot/prompts.py`
- `app/pole_api/src/analyst_chatbot/tools.py`
- `app/pole_api/tests/test_analyst_capabilities_tool.py` (or existing capability test module — find it and extend)
