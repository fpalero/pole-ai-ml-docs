# Ticket: PAIML-POLE-API-140

## Title
md-first structural enforcement in shaping (deterministic template fallback)

- **Status**: 📋 PLANNED
- **Project**: pole_api (analyst chatbot shaping)
- **Phase**: 42 coach-gate-25
- **Blocks**: —
- **Blocked By**: — independent of 141 (none block each other).

## Context

Local SAMPLE-5 gate 21/25 (run `20260923-205700`, report
`docs/app/pole_api/phase-42-coach-gate-25/LOCAL_GATE_20260923_2125.md` — binding
evidence). PR-02 / PR-04 fail systematically on the `md-first` assertion:
answers lead with `progress_matrix` instead of prose.

Root cause (proven by live code execution): `sanitize_blocks`
(`app/pole_api/src/analyst_chatbot/blocks.py:898-904`) drops md blocks with
empty/falsy content. When the model emits leading empty prose, the strip
promotes the data block to `blocks[0]`, violating the documented md-first
block vocabulary (`coach-150q.spec.ts:92`). `ensure_tool_blocks` only appends
and cannot restore order. Tickets 134/135/136 diffed for ordering changes:
none. Same nondeterminism family as 135's blanks, at block level.

USER DECISIONS (binding): deterministic template fallback — NOT an LLM repair
loop (a header sentence carries no information; synthesizing beats
re-prompting), NOT prompt-only (probabilistic). A grounded-summary middle
layer was explicitly REJECTED.

## Scope

1. **Structural enforcement in shaping (after `sanitize`, before return):**
   - Drop whitespace-only md blocks (`content.strip() == ""`).
   - If `blocks[0]` isn't `md`, prepend a synthesized context-aware header
     (exact strings per flow, table below — `{trick}` = resolved trick name;
     trick unknown → trick-less variant).
2. **Prompt instruction** in the progress turn (and any turn composing data
   blocks): open with 1–2 sentence prose before data. Best-effort only —
   the shaping fallback is the guarantee.
3. **Unit tests:** empty / whitespace-only / missing leading prose →
   md-first holds; real prose untouched; header wording per flow.

Header strings (exact, binding):

| flow | `{trick}` known | trick unknown |
| :--- | :--- | :--- |
| progress | `Here's your {trick} progress summary.` | `Here's your progress summary.` |
| video_analysis | `Here's your {trick} video analysis summary.` | `Here's your video analysis summary.` |
| training_plan | `Here's your {trick} training plan summary.` | `Here's your training plan summary.` |
| injury | `Here's your {trick} injury-prevention summary.` | `Here's your injury-prevention summary.` |
| readiness | `Here's your {trick} readiness summary.` | `Here's your readiness summary.` |
| unknown/other | `Here's your summary.` | `Here's your summary.` |

Out of scope: changing block content beyond ordering + header insert; LLM
repair loops; grounded summaries; touching 134 tier semantics.

## Validation Plan

1. Unit tests: `pytest -k md_first` (or shaping/block suite) green —
   empty / whitespace-only / missing leading prose → `blocks[0].type == "md"`;
   real leading prose passes through byte-identical.
2. Repeated progress-turn runs: PR-02 / PR-04 `md-first` assertion green
   across repeated runs (nondeterminism absorbed by construction).
3. No regression: other flows' `blocks[0]` unchanged when model emits real
   prose (existing shaping tests green).

## Acceptance Criteria

- [ ] PR-02 / PR-04 green across repeated runs.
- [ ] `md-first` assertion deterministic by construction (shaping guarantees
      `blocks[0]` is `md` regardless of model prose emission).
- [ ] No change to block content beyond ordering + header insert.
- [ ] Header wording matches the per-flow table exactly.
- [ ] Real model prose never rewritten or replaced.

## Dependencies

- **Blocked By**: —.
- **Blocks**: —.

## Estimated Effort

- [S] (shaping guard + prompt line + unit tests)
