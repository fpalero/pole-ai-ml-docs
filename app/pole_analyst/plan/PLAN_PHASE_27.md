# Fase 27 — Question-card status chip (status ONLY on user question card) — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Backend requerido: ninguno nuevo —
> reutiliza la señal de error `pole_api` Phase 29 (`PAIML-POLE-API-093`, item (d))
> y el contrato de retry de `PAIML-POLE-ANALYST-073`.
> Grounding RAG: `src/app/core/chat-state/chat-state.ts`,
> `src/app/core/services/chatbot.service.ts`,
> `src/app/features/chat/components/chat-pane/chat-pane.component.ts`;
> tickets `PAIML-POLE-ANALYST-004/007/008`; Phase 24
> ([PLAN_PHASE_24](PLAN_PHASE_24.md)).

## Contexto

El chat pane rinde hoy una burbuja de pensamiento standalone ("thinking bubble")
además del estado del turno. Decisión de UX aprobada por el usuario: eliminar la
burbuja standalone y mostrar el estado **SOLO como chip sobre la tarjeta de la
pregunta del usuario** (question card). Los estados llegan por el WS existente
(`ChatState` Idle|Thinking|Working|Completed|Error; eventos
`connected`/`message_sent`/`job_started`/`job_progress`/`agent_reply`/`error`)
y el comportamiento live del WS no cambia (`ChatbotService.state$` +
`ChatbotSocketService`).

`PAIML-POLE-ANALYST-078` **supersede la parte thinking-bubble** de
`PAIML-POLE-ANALYST-073` (la burbuja standalone desaparece) pero **reutiliza su
contrato de retry** (re-send vía `ChatbotService.sendMessage`, composer path,
deshabilitado en Thinking/Working).

## ADR — por qué el chip se mueve a la question card

- **Contexto:** dos superficies mostraban estado (burbuja standalone +
  chip/bubble del turno) y podían contradecirse; la burbuja de error de 073 se
  solapaba con contenido (Phase 24: "error bubble overlaps").
- **Decisión:** una única superficie de estado — chip anclado a la tarjeta de
  la pregunta del usuario que originó el turno. Sin burbuja standalone.
- **Alternativas consideradas:**
  - *Mantener burbuja + chip:* rechazado — doble fuente de verdad, solapes.
  - *Chip en la respuesta del agente:* rechazado — el estado pertenece a la
    pregunta (el turno aún no tiene respuesta mientras Thinking/Working).
- **Consecuencias:** el componente del chip debe ser reutilizable (futuras
  apps); terminal `Completed` rinde "Answered ✓ + timestamp" y terminal `Error`
  rinde texto de error + botón Retry sobre la misma tarjeta.

## Tickets

| Ticket | Scope | Estado |
| :--- | :--- | :--- |
| `PAIML-POLE-ANALYST-078` | [Presentation] Question-card status chip: quitar thinking bubble, chip reutilizable en user card (Idle/Thinking/Working/Completed/Error), terminal Answered ✓ + timestamp, error + Retry vía composer path, tokens + aria-labels, sin leaks | 📋 PLANNED |

## Tasks

1. **Quitar thinking bubble** — eliminar la burbuja standalone del chat pane;
   el estado se rinde solo en el chip de la question card.
2. **Chip reutilizable** — nuevo componente standalone (p. ej.
   `question-status-chip`) con `@Input() state: ChatState` (+ timestamp/error);
   estilos con tokens de compañía (`app.scss`/`design-tokens`); English only.
3. **Cablear estados live** — consumir `ChatbotService.state$` existente
   (Idle|Thinking|Working|Completed|Error desde `chat-state.ts`); sin cambios
   al WS (`ChatbotSocketService`); `takeUntilDestroyed`, sin leaks.
4. **Terminales** — `Completed` → "Answered ✓ + timestamp" en la user card;
   `Error` → texto de error + botón Retry en la user card.
5. **Retry** — reutilizar contrato 073: re-send vía `ChatbotService.sendMessage`
   (composer path), deshabilitado en Thinking/Working.
6. **A11y + specs** — aria-labels WCAG 2.1 AA por estado; specs UC-04
   (Idle→Thinking→Working→Completed) + error+retry; ≥ 80% cobertura.
7. **Checks** — `npx ng test --watch=false` verde, `lint` limpio, `build`
   typecheck OK.

## Acceptance

- Sin burbuja standalone en el chat pane; estado visible solo en la question card.
- Transición live Idle→Thinking→Working→Completed (UC-04) sobre la user card.
- `Completed` muestra "Answered ✓ + timestamp"; `Error` muestra error + Retry funcional.
- Retry usa el composer path; deshabilitado en Thinking/Working.
- Componente reutilizable, tokens de compañía, English only, aria-labels AA, sin leaks.
- `ng test`/`lint`/`build` verdes.

## Dependencies

- **Blocks:** None.
- **Blocked By:** None (interno). Relacionado: `PAIML-POLE-API-093` (señal de
  error) y `PAIML-POLE-ANALYST-073` (contrato de retry reutilizado; 078
  supersede su parte thinking-bubble).
