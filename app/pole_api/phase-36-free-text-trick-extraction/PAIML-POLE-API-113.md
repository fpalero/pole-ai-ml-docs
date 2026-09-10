# Ticket: PAIML-POLE-API-113

## Title
Route progression to catalog-first: QUERY_DOMAINS + catalog, P4 prompt example

## Status
📋 PLANNED

## Description
Even with `trick_name` resolved (112), the query graph cannot answer
progression from the catalog: `QUERY_DOMAINS`
(`packages/pole_coach/src/pole_coach/graphs/query.py:48`) excludes the
catalog domain. The catalog holds 447 moves; the `handspring` entry declares
6 forward transitions (Inverted-Crucifix, Butterfly, Flatline, Hangglider,
Iron-X, Gemini) — the exact "what next" candidates.

What to do (no code in this ticket — spec for the implementer):

- [ ] Include the `catalog` domain in `QUERY_DOMAINS` for the progression
  route (catalog-first for "which other trick / what next" intents; RAG
  stays as supplement, not primary).
- [ ] P4 prompt example: handspring → list the 6 forward transitions as
  candidates (grounded in catalog entry, never hallucinated).
- [ ] Keep non-progression routes unchanged (no domain bleed).

## Files Affected
- `packages/pole_coach/src/pole_coach/graphs/query.py` (`QUERY_DOMAINS`)
- Progression prompt (P4 — `pole_coach` prompts / analyst prompt carrying
  the P4 example; implementer to locate current P4 file)
- Routing tests (implementer to co-locate with query-graph tests)

## Unit-Test Requirement
- [ ] Progression intent + resolved `handspring` → route includes `catalog`
  domain.
- [ ] Non-progression intents → domains unchanged (no catalog bleed).
- [ ] P4 example renders the 6 handspring forward transitions verbatim
  from the catalog entry.

## Integration Tests
- [ ] Handspring progression turn (post-112 state) → catalog-first path
  fires; candidates ⊆ {Inverted-Crucifix, Butterfly, Flatline, Hangglider,
  Iron-X, Gemini}.
- [ ] `pixi run test-api` green (plus `pole_coach` suite if touched).

## Acceptance Criteria
- [ ] UC-02: progression question with `handspring` routes catalog-first.
- [ ] Candidates come from the catalog entry's forward transitions — no
  hallucinated trick names.
- [ ] No regression on non-progression query routes.

## Dependencies
- **Blocks**: none.
- **Blocked By**: PAIML-POLE-API-112 (needs resolved `trick_name`).

## Estimated Effort
- [S]
