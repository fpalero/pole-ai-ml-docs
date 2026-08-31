# Fase 2 — Chat Pane (left) — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md)

## Tareas

- [ ] Infra `ChatbotSocketService`: conectar a `/api/chatbot/ws/chat`, enviar `{type:"message",message,session_id?}` y `{type:"resume",session_id}`, parsear server frames, auto-reconnect (exponential backoff) + `session_id` resume tras caída.
- [ ] App derivar `ChatState` de frames: `connected`→Idle, en `message` send→Thinking, `job_started`/`job_progress`→Working, `agent_reply`→Completed, `error`→Error.
- [ ] Presentation message list (user/assistant bubbles), `StatusChip` junto al header "Coach", composer input + send.
- [ ] Test unit tests T2.x (frame→state mapping, reconnect, resume).

## Criterios de aceptación

- [ ] Chat pane funcional con WS resiliente; tests T2.x verdes (UC-04).