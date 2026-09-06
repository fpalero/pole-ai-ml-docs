# Fase 25 — Analysis summary plain language — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Origen: user-reported defect from manual
> staging testing (summary section renders technician prose). Tone reference:
> phase 22 (`PAIML-POLE-ANALYST-071` — coach plain-language chat).

## Contexto

La sección de summary del análisis (`features/analysis` — composer en
`app/pole_analyst/src/app/features/analysis/models/summary.ts`) compone hoy una
frase de técnico desde datos live (formato hardcodeado, valores live), p. ej.
"339 deviations detected — most critical: torso_tilt_speed in the Hold phase
(z=-20, frame 316) — overall score 88/100." Y `summary.spec.ts` (líneas
~129-183) fija ese jargon como salida esperada, bloqueando el fix.

El usuario necesita frases de coach human-understandable ONLY: sin metric ids
`snake_case` (mapear a nombres humanos, e.g. `torso_tilt_speed` → torso
control), sin z-scores, sin números de frame, sin conteos crudos de
desviaciones; el overall score puede quedarse; tono phase-22.

## Tickets

| Ticket | Scope | Estado |
| :--- | :--- | :--- |
| `PAIML-POLE-ANALYST-074` | Rewrite `summary.ts` composer a coach sentences + mapa human-name; update `summary.spec.ts` (single/multiple/positive); 4 before/after normativos en el ticket | 📋 PLANNED |

## Tasks

1. **Composer rewrite** — `summary.ts`: mismas entradas live (`scores`,
   `detections`, `critical_*`, fases), nueva plantilla plain; mapa central
   metric-id → human-name con fallback genérico (nunca raw id).
2. **Jargon strip** — en el boundary del composer: ni metric ids, ni
   z-scores, ni frame numbers, ni deviation counts (incl. tooltips/titles de
   esta sección).
3. **Specs** — reemplazar expectativas de jargon en `summary.spec.ts`
   (~129-183) por asserts plain (single / multiple / positive); ≥ 80%
   cobertura.
4. **Score + fases** — mantener overall score; nombres de fase humanos.
5. **Checks** — `npx ng test --watch=false` verde, `lint` limpio, `build`
   typecheck OK.

## Acceptance

- Summary rinde solo coach sentences (specs lo asertan: sin `snake_case`,
  sin z, sin frame, sin counts, en todos los estados).
- Mapping aplicado (`torso_tilt_speed` → torso control); ids desconocidos
  nunca leakean raw.
- Overall score visible; tono phase-22.
- Tests verdes + lint + build.

## Dependencies

- **Blocks:** None.
- **Blocked By:** None (FE-only; referencia de tono: `PAIML-POLE-ANALYST-071`).
