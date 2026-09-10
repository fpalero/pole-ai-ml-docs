# Ticket: PAIML-POLE-API-114

## Title
Answer shaping "what next" + UC coverage incl. bank #27

## Status
📋 PLANNED

## Description
With extraction (112) and catalog-first routing (113) in place, the reply
itself must be shaped: a "what next" answer listing candidate tricks from
the catalog forward transitions (with a low-confidence disclaimer when
applicable) — never the `unknown` gating fallback when a trick was provided
in any channel. Must also cover the user-selected bank item #27:
*"Analyse my latest handspring video and tell me what to focus on first"*
— the video+trick focus case where the video label takes precedence and the
answer is ordered focus points, not a trick list.

What to do (no code in this ticket — spec for the implementer):

- [ ] "What next" shaping: candidates from forward transitions + one-line
  why-each (catalog-grounded); low-confidence/no-video disclaimer when the
  trick came from text only.
- [ ] Bank #27 shaping: video present → focus-first answer (ordered focus
  points from analysis/coach insights); video label precedence over any
  text mention asserted.
- [ ] Never emit the `unknown` "No trick name was provided…" reply when
  `trick_name` was resolved via any channel.

## Files Affected
- Answer-shaping path (analyst formatter / `convert_supergraph_blocks`
  fallback templates — implementer to locate; shared with 111 contract)
- UC/bank coverage tests (implementer to co-locate, incl. bank #27)

## Unit-Test Requirement
- [ ] Resolved trick + catalog candidates → "what next" reply lists
  candidates, no `unknown` fallback text.
- [ ] Bank #27 (video + handspring label) → focus-first reply shape;
  video label precedence asserted.
- [ ] Genuine `None` (no trick in any channel) → existing `unknown` path
  preserved (not swallowed by shaping).

## Integration Tests
- [ ] Bank #27 end-to-end (video): focus points ordered, no `unknown`
  fallback.
- [ ] Text-only handspring progression: "what next" with the 6 catalog
  candidates.
- [ ] `pixi run test-api` green.

## Acceptance Criteria
- [ ] UC-03 / bank #27: *"Analyse my latest handspring video and tell me
  what to focus on first"* → video-label precedence + ordered focus
  answer.
- [ ] Text-only progression → "what next" candidate list, catalog-grounded.
- [ ] `unknown` gating reply only when no channel provided a trick.

## Dependencies
- **Blocks**: none.
- **Blocked By**: PAIML-POLE-API-112 (needs resolved `trick_name`).

## Estimated Effort
- [S]
