# Ticket: PAIML-POLE-API-112

## Title
Deterministic free-text trick extraction in `_build_state`

## Status
📋 PLANNED

## Description
`SupergraphAnalystAgent._build_state`
(`app/pole_api/src/analyst_chatbot/coach_providers.py:742-774`) only sets
`trick_name` from the video histogram label. A free-text turn like *"I am
able to do the handspring. Which other trick can I try now?"* (no video)
yields `trick_name=None`, and downstream `pole_coach` gating
`resolve_trick(None)` returns `unknown` — *"No trick name was provided…"*
(`packages/pole_coach/src/pole_coach/gating.py:101-110`).

WHY it was missing (ADR): `_build_state` was designed video-centric —
`trick_name` was a video attribute (via histogram), never a user mention in
free text. Progression/readiness is the first flow where the trick lives
only in the user's sentence. Fix is deterministic extraction (catalog as
vocabulary) in `_build_state`, ahead of gating, with no `pole_coach`
changes: the coach keeps receiving a resolved `trick_name` or a genuine
`None` (no trick mentioned in any channel).

What to do (no code in this ticket — spec for the implementer):

- [ ] New deterministic helper `extract_trick_from_text(text,
  catalog_names)`: lowercase + hyphen/space-insensitive match against
  catalog move names/aliases; first/longest match wins; no LLM, no network.
- [ ] Wire into `_build_state` with precedence: **video label > free text >
  `None`**. Free-text extraction only fires when the video provides no
  label (bank #27 video case keeps video precedence).
- [ ] Ambiguous/no-match → `None` (genuine unknown flows to existing
  gating unchanged).

## Files Affected
- `app/pole_api/src/analyst_chatbot/coach_providers.py` (`_build_state`,
  + new helper — suggest `app/pole_api/src/analyst_chatbot/trick_mentions.py`)
- `app/pole_api/tests/test_trick_extraction*.py` (new)

## Unit-Test Requirement
- [ ] Handspring sentence (no video) → `trick_name=handspring`.
- [ ] Case/hyphen variants (`"Hand-Spring"`, `"HANDSPRING"`) → same match.
- [ ] Video label present + conflicting text mention → video label wins.
- [ ] No trick mentioned anywhere → `None` (gating `unknown` path
  preserved).
- [ ] No LLM calls; catalog names mocked/fixture-driven.

## Integration Tests
- [ ] Analyst turn without video, handspring sentence → state carries
  `trick_name=handspring` into the supergraph (no `unknown` gating reply).
- [ ] Bank #27 turn with video → video label precedence asserted
  end-to-end (covered jointly with 114).
- [ ] `pixi run test-api` green.

## Acceptance Criteria
- [ ] UC-01: *"I am able to do the handspring. Which other trick can I try
  now?"* (no video) resolves `trick_name=handspring` deterministically.
- [ ] Precedence video > text > `None` asserted in tests.
- [ ] `pole_coach` untouched (no `gating.py` changes).

## Dependencies
- **Blocks**: PAIML-POLE-API-113, PAIML-POLE-API-114.
- **Blocked By**: none.

## Estimated Effort
- [S]
