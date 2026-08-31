# Fase 11 — Analyst chatbot UI (WS `/ws/analyst-chat`) — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md) · Feature: detección automática de fases (handspring) — FE `pole_analyst`

## Contexto

La Fase 2 (Chat Pane) consume `/api/chatbot/ws/chat` (training chatbot). Esta fase cambia el chat al
nuevo **analyst chatbot** (`/ws/analyst-chat`) con herramientas de histogramas, clasificación
(solo-classify) y edición de imágenes (extract frames, crop). El chat es para conversación sobre el
feedback y el improvement plan; no produce el histograma.

## Alcance

### 1. Cliente WS del analyst chatbot

- Conectar a `/ws/analyst-chat`; frames: `connected`, `agent_reply`, `session_resumed`, `error`,
  relaid `job_*` (mismo wire protocol que `/ws/training-chat`).
- Auto-reconnect + `session_id` resume (reutiliza `ChatbotSocketService` de la Fase 2).

### 2. Tool-call chips

- Renderizar tool calls: `histogram` (análisis de histogramas), `classify` (solo clasificación),
  `extract_frames` / `crop` (edición de imágenes).
- Enlazar artefactos (imágenes de frames) devueltas por las tools.

## Endpoints consumidos

| Endpoint | Método | Uso |
| :--- | :--- | :--- |
| `/ws/analyst-chat` | WebSocket | Conversación + tools del analyst |

## Tickets (candidatos)

- [ ] **PAIML-POLE-ANALYST-036** — App/Domain: servicio WS analyst + DTOs de tool calls.
- [ ] **PAIML-POLE-ANALYST-037** — Presentation: tool-call chips + artefactos de imagen.
      Blocked by backend `PLAN_PHASE_4` (analyst chatbot slice).

## Dependencias

- **Blocked By:** backend `pola_api` fase 4; FE fases 2 y 8-10.

## Criterios de aceptación

- [ ] Chat conecta a `/ws/analyst-chat` con resume.
- [ ] Las tools (histogram/classify/extract_frames/crop) se renderizan como chips con artefactos.
- [ ] Cobertura ≥ 80% en módulos nuevos.