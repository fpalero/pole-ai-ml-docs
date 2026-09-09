# Fase 23 — FE chat cards (score_summary / phasic_feedback / metric_matrix / drills / quick_replies) — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Backend requerido: `pole_api` Phase 28
> (`analyst_chatbot/blocks.py`, `PAIML-POLE-API-087` — block shapes)

## Contexto

The analyst chatbot chat pane (`app/pole_analyst`, `features/chat/components/chat-pane/chat-pane.component.ts`,
inline template) renders `md` / `video_segment` / `analysis_link` / `image` today and falls into a `@default`
placeholder for the five structured block types the backend already produces. The block model is complete in
`core/models/api.models.ts` (`ChatAnswerBlock` union); the FE just never renders these five.

Backend block shapes (`analyst_chatbot/blocks.py`, `PAIML-POLE-API-087`, phase-28):

- `score_summary`: `{score: int, max: int, classification, summary?}`
- `phasic_feedback`: `{items: [{phase_title, status: Consistent | Needs Adjustment | Optimal Form, description, timestamp?}]}`
- `metric_matrix`: `{title?, rows: [{parameter, benchmark_target?, recorded_value?, variance?, assessment?}]}`
- `drills`: `{items: [{title, description, drill_id?, sets_reps?}]}`
- `quick_replies`: `{replies: string[]}`

## Tickets

| Ticket | Scope | Estado |
| :--- | :--- | :--- |
| `PAIML-POLE-ANALYST-072` | Render the 5 missing chat cards + quick-reply send path + unit tests | 📋 PLANNED |

## Tasks

1. **score_summary card** — Stitch Kinetic Score badge style: `score`/`max` + `classification` + optional
   `summary`. Reuse design tokens (`app.scss`/`design-tokens`), WCAG 2.1 AA aria labels.
2. **phasic_feedback card** — rows with status chip (`Consistent` | `Needs Adjustment` | `Optimal Form`),
   `phase_title` + `description` + optional `timestamp`.
3. **metric_matrix card** — optional `title` + table (`parameter`, `benchmark_target`, `recorded_value`,
   `variance`, `assessment`).
4. **drills card** — `title` + `description` + `sets_reps` (optional `drill_id` for keying only, never raw JSON).
5. **quick_replies pills** — pill list from `replies: string[]`; click sends the text via
   `ChatbotService.sendMessage` (reuse the composer path, disable while state Thinking/Working).
6. **Unit tests** — cover all five renderers in the chat-pane specs (or child card components), ≥ 80%
   coverage; aria-label checks; design-token classes asserted.
7. **"New conversation" reset action in the chat-pane header** — clears local messages and starts a fresh
   WS session (disconnect + reconnect WITHOUT sending the resume frame / without session_id), per the
   analyst chatbot WS protocol. Must work from any state (Idle/Thinking/Working/Error), be disabled
   while Thinking/Working or no-op safe, include aria-label/WCAG styling with design tokens, and be
   covered by unit tests (chat-state / chat-pane spec).

## Acceptance

- Each block type renders its card when present in `agent_reply.blocks`.
- Unknown types keep the existing `@default` placeholder (never raw JSON — cf. Phase 22 guard).
- Quick pill click sends the message via the composer path; disabled while Thinking/Working.
- No subscription leaks (`takeUntilDestroyed`).
- Long-session guard: a reset round-trip yields a new ws_connection_id/session (no resume), and a
  40-question UI drive does not hit context saturation (questions after ~15 do not fall back) — reset
  between chunks.
- `npx ng test --watch=false` green, `npx ng lint` clean, `npx ng build` typecheck passes.

## Dependencies

- **Blocks:** None.
- **Blocked By:** None (backend `PAIML-POLE-API-087` phase-28 already shipped the block shapes; FE renders
  against that contract with mock/stub until wired in E2E).

---

## Supplementary Stitch design context (from `feature/PAIML-POLE-DOCS-023-answer-cards`, kept per keep-both rule)

> Origen: Stitch "Pole AI Coach" Multimodal Analysis Answer Card + backend contract
> `PAIML-POLE-API-090` Task 6 (`pole_api` Phase 30), which defines the structured block
> vocabulary (`score_summary`, `phasic_feedback`, `metric_matrix`, `drills`,
> `quick_replies`, `image`). FE-only: renderiza esos bloques como las secciones de la
> tarjeta Stitch en el chat pane.

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

Supplementary tasks (Stitch parity, from incoming side):

- Componentes/card por tipo de bloque (`score_summary`, `phasic_feedback`, `metric_matrix`,
  `drills`, `quick_replies`, `image` con phase tag + chips); header metadata + feedback
  footer (thumbs) si está en el diseño.
- Integración en `chat-pane.component.ts` + actualización del modelo
  `chat-message.ts`; preservar el fallback gracioso de bloques desconocidos (API-090 6c).
- Paridad desktop + mobile (variantes Stitch `e6a43…` / `ed50e…` / `81533…`); pills
  quick-reply como sugerencias FE-only (sin llamadas backend); unit tests ≥ 80% +
  Playwright spec.
- Sin regresiones en features de chat existentes (video_segment, image, md, fallback 071).

Supplementary acceptance (Stitch parity):

- Cada sección de la tarjeta renderiza desde su JSON de bloque; fallback desconocido
  preservado; paridad vs Stitch; WCAG 2.1 AA; `ng test` / `lint` / `build` + Playwright
  en verde contra `pola_api` con DBs `_testing` + `E2E_FAKES=1`.

Supplementary dependency note (incoming side; prose only, team-lead release gate):
Starts after `PAIML-POLE-API-090` merges (team-lead release gate; cross-project, not
enforced by crew-validate). No se declara un `Blocked By` formal cross-project.
