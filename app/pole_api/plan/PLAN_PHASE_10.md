# Fase 10 — Production hardening — 🟡 PARTIAL / FUTURE

> Plan maestro: [PLAN.md](PLAN.md)

## Alcance

- Secretos fuera de código (env vars), CORS produccion, rate limiting, logging estructurado,
  métricas de API.
- Deployment manifests (Kubernetes `infrastracture/`).
- Optimización de jobs (pool size, memoria) para cargas reales.
- WebSocket routers condicionales (montado solo si deps de `pole_chatbot` presentes).

## Estado

- **PARTIAL / FUTURE** — hardening parcial; trabajo restante por priorizar.

## Dependencias

- Fases 1-9.

## Criterios de aceptación

- Despliegue produccion con secretos externos + métricas.