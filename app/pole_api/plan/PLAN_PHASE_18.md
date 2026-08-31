# Fase 18 — Analyst chatbot (WS `/ws/analyst-chat`) — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md) · Feature: detección automática de fases (handspring) — backend

## Contexto

Nuevo slice **`analyst_chatbot`**: chatbot conversacional para el atleta/coach que consulta
histogramas, clasifica trucos y edita imágenes (extract frames, crop). Usa el patrón del
`training_chatbot` (ReActAgent + `ChatbotSessionService`).

## Alcance

### 1. Slice `analyst_chatbot`

- `analyst_chatbot/router.py` + `services.py` + `sessions.py` (espejo de `training_chatbot`).
- WS `/ws/analyst-chat` — wire protocol idéntico a `/ws/training-chat`:
  - Client→server: `{"type":"message","message":"…"}`, `{"type":"resume","session_id":S}`.
  - Server→client: `connected`, `agent_reply`, `session_resumed`, `error`, y **job events relaid**
    (`job_started`, `job_progress`, `job_done`, `job_error`).
- Sesiones persistidas (`chatbot sessions`), resume tras reconnect.
- `AnalystFacade` — integra las tools del analyst.

### 2. Tools del analyst

- `histogram` — análisis de histogramas del video (lee `skeleton_video_signals` + cohort).
- `classify` — **solo clasificación** (LSTM) de un video.
- `extract_frames` — extraer frames del video (devuelve `frame_image_path`s).
- `crop` — recortar/seleccionar segmento del video.
- El chat NO produce el histograma (eso lo hace el FE vía `POST /api/analysis/videos/{id}/analyze`);
  el chatbot es conversación + consulta + edición.

### 3. Frames relaid

- Los eventos de job del análisis (pipeline) se relayan al WS para que el FE sincronice el progress
  panel (etapas Extraction→Processing→Phase detection→Classification & analysis→Summary).

## Tickets (candidatos)

- [x] **PAIML-POLE-API-050** — Slice `analyst_chatbot` (router + services + sessions) + WS
      `/ws/analyst-chat`.
- [ ] **PAIML-POLE-API-051** — Tools `histogram`, `classify`, `extract_frames`, `crop` +
      `AnalystFacade`.
- [ ] **PAIML-POLE-API-052** — Relaying de job events del análisis al WS + resume de sesiones.

## Dependencias

- Fases 13 (analysis slice), 16 (referencias), 17 (detección).
- Reutiliza: `training_chatbot` (ReActAgent, `ChatbotSessionService`).

## Criterios de aceptación

- WS `/ws/analyst-chat` funcional con resume y job events relaid.
- Tools `histogram`/`classify`/`extract_frames`/`crop` invocables vía ReActAgent.