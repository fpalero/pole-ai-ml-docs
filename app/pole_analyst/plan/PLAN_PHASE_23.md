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

## Acceptance

- Each block type renders its card when present in `agent_reply.blocks`.
- Unknown types keep the existing `@default` placeholder (never raw JSON — cf. Phase 22 guard).
- Quick pill click sends the message via the composer path; disabled while Thinking/Working.
- No subscription leaks (`takeUntilDestroyed`).
- `npx ng test --watch=false` green, `npx ng lint` clean, `npx ng build` typecheck passes.

## Dependencies

- **Blocks:** None.
- **Blocked By:** None (backend `PAIML-POLE-API-087` phase-28 already shipped the block shapes; FE renders
  against that contract with mock/stub until wired in E2E).
