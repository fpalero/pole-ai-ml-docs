# Ticket: PAIML-POLE-API-117

## Title
Explicit unknown-trick reply on the query-graph path (batch-1 Q3 residual)

## Status
📋 PLANNED

## Description
Phase 36 staging gate (image `8425896` FRESH, batch-1 `20260910-231630`):

- **Q:** *"I can do the moonflip-9000, what should I try next?"*
- **A (verbatim):** *"I couldn't build full coaching advice from the
  available data right now. Please try again with a video or a trick name
  so I can analyse your session."* — 0 tool calls, `block_types: ["md"]`.
- Evidence: `app/pole_analyst/test-results/coach-150q/batch1-20260910-231630/batch1-transcript.jsonl`
  (`BATCH1-Q3`), frames in `batch1-frames.json`.

Lo correcto: el turno resuelve `unknown` con cero fabricación
(`moonflip-9000` no existe en el catálogo de 447). Lo que falta: el path
del query-graph renderiza el fallback genérico desnudo en vez de la guía
explícita *"Unknown trick 'moonflip-9000'…"* que solo existe en
`gating.resolve_trick` + el finish path de readiness. El usuario recibe
un callejón sin salida en lugar de una guía accionable (qué trucos sí se
reconocen, cómo pedir progresión válida).

What to do (no code in this ticket — spec for the implementer):

- [ ] Rutar turnos de progresión con truco unknown a readiness, O añadir
      el reply explícito de unknown-trick en el fallback del query-graph
      (fraseo de progresión + mención resoluble-pero-desconocida:
      el truco se resolvió como unknown, no es un fallo de datos).
- [ ] MUST NEVER fabricate transitions: ningún candidato "next trick",
      ninguna transición forward inventada para un truco desconocido.
- [ ] Mantener el 107 terminal fallback solo para turnos genuinamente
      irresolubles (este turno es resoluble-como-unknown, no irresoluble).

## Files Affected
- `packages/pole_coach` query graph fallback + readiness finish path
  (`gating.resolve_trick` como referencia del texto explícito;
  implementer to locate; coordinar con 113 — mismos ficheros de ruteo)
- tests: unknown-trick progression reply (new, co-located)

## Unit-Test Requirement
- [ ] Progression turn, trick resolves unknown → explicit
      `Unknown trick '…'…` reply (progression phrasing), assert zero
      forward-transition candidates emitted.
- [ ] Genuinely unresolvable turn → existing generic/terminal path
      preserved (no regression to 107).

## Integration Tests
- [ ] Re-run staging Q3 only (`moonflip-9000` progression) green:
      explicit unknown-trick guidance, no bare "couldn't", no fabrication.
- [ ] `pixi run test-api` green.

## Acceptance Criteria
- [ ] Q3 answers with the explicit unknown-trick guidance (names the
      unknown trick, points to recognizable tricks / valid progression
      requests).
- [ ] Zero fabricated transitions for unknown tricks.
- [ ] No regression to known-trick progression (handspring → 6 catalog
      transitions, per 113/114).

## Dependencies
- **Blocks**: none.
- **Blocked By**: none (independent of PAIML-POLE-API-118).

## Estimated Effort
- [S]
