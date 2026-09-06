# Fase 23 — Stitch Chatbot Answer Cards (structured blocks) — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Origen: Stitch "Pole AI Coach" Multimodal Analysis
> Answer Card + backend contract `PAIML-POLE-API-090` Task 6 (`pole_api` Phase 30), which
> defines the structured block vocabulary (`score_summary`, `phasic_feedback`,
> `metric_matrix`, `drills`, `quick_replies`, `image`). Esta fase es FE-only: renderiza
> esos bloques como las secciones de la tarjeta Stitch en el chat pane.

## Contexto

`PAIML-POLE-API-090` Task 6 (6b) extiende `blocks.py` `VALID_TYPES` y el
`ANALYST_SYSTEM_PROMPT` con tipos de bloque estructurados que mapean 1:1 a las secciones
de la tarjeta Stitch, y (6c) deja un fallback gracioso para bloques desconocidos. Esta
fase construye el renderizado completo de la tarjeta en `app/pole_analyst`: componentes
Angular por tipo de bloque, variantes desktop + mobile, y paridad de diseño con las
pantallas Stitch. Referencia de diseño (sin pegar HTML): `/tmp/opencode/stitch-cards/`
(`answer-card.html`, `answer-card-desktop.png`, `chat-mobile.html`); pantallas del
proyecto Stitch "Pole AI Coach" — tarjeta desktop `e6a4363e82ac4a5db060426f97ae0bdd`,
variante mobile `ed50e9f93f3748b98a3f62ad31c65883`, chat mobile `8153376de3af4761875082b8950fd49a`.

Secciones a renderizar (bloque → sección Stitch):

| Bloque | Sección Stitch |
| :--- | :--- |
| `score_summary` | Executive summary + Kinetic Score badge (Class A Performance) |
| `image` (phase_label, chips) | CV telemetry image frames — 2-col bento con phase tag + metric chips |
| `phasic_feedback` | Key Movement Observations / phasic feedback list |
| `metric_matrix` | Biomechanical Metric Variance Matrix (tabla) |
| `drills` | Prescriptive Corrective Protocol drill cards |
| `quick_replies` | Quick-reply action pills |
| `video_segment` (existente) | Mobile video-reference card (reutiliza el render actual) |

Convenciones framework (de `pole_fe`, ver Sibling reference en PLAN.md): Angular 22,
vitest (`npx ng test --watch=false`, ≥ 80% coverage), Playwright E2E, SignalStore,
Tailwind, WCAG 2.1 AA.

## Tickets

| Ticket | Scope | Estado |
| :--- | :--- | :--- |
| `PAIML-POLE-ANALYST-072` | Render tarjeta-respuesta Stitch por bloques estructurados (desktop + mobile) | 📋 PLANNED |

## Tasks

- Componentes/card por tipo de bloque (`score_summary`, `phasic_feedback`, `metric_matrix`,
  `drills`, `quick_replies`, `image` con phase tag + chips); header metadata + feedback
  footer (thumbs) si está en el diseño.
- Integración en `chat-pane.component.ts` + actualización del modelo
  `chat-message.ts`; preservar el fallback gracioso de bloques desconocidos (API-090 6c).
- Paridad desktop + mobile (variantes Stitch `e6a43…` / `ed50e…` / `81533…`); pills
  quick-reply como sugerencias FE-only (sin llamadas backend); unit tests ≥ 80% +
  Playwright spec.
- Sin regresiones en features de chat existentes (video_segment, image, md, fallback 071).

## Acceptance

- Cada sección de la tarjeta renderiza desde su JSON de bloque; fallback desconocido
  preservado; paridad vs Stitch; WCAG 2.1 AA; `ng test` / `lint` / `build` + Playwright
  en verde contra `pola_api` con DBs `_testing` + `E2E_FAKES=1`.

## Dependencies

- **Blocks:** None.
- **Blocked By (prose only, team-lead release gate):** Starts after `PAIML-POLE-API-090`
  merges (team-lead release gate; cross-project, not enforced by crew-validate). No se
  declara un `Blocked By` formal cross-project.
