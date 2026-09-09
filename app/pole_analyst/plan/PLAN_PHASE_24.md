# Fase 24 — FE failed-turn error state + image endpoint URLs — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Backend requerido: `pole_api` Phase 29
> (`PAIML-POLE-API-093` — señal de error (d) + endpoint de imágenes (a)). Evidencia del tester
> (local, no commiteada): `/tmp/opencode/tool08-repro/tool08-frames.json`,
> `/tmp/opencode/staging-battery/summary.json`.

## Contexto

El chat pane (`features/chat/components/chat-pane/chat-pane.component.ts`, inline template)
rinde hoy los turnos ABANDONED/error como una burbuja `md` normal con chip `Completed`
(`tool08-frames.json`: `"chipFinal": "Completed"`, `agent_reply` con fallback genérico
"I'm having trouble understanding…" y `tool_calls: []`). El usuario no distingue un fallo de
una respuesta y no tiene vía de retry. El backend Phase 29 emite ahora una señal de error
explícita legible por máquina en el frame `agent_reply` (item (d)) y sirve los artefactos por
endpoint HTTP con URLs alcanzables en `image.src` (item (a)).

## Tickets

| Ticket | Scope | Estado |
| :--- | :--- | :--- |
| `PAIML-POLE-ANALYST-073` | Error bubble/chip + retry sobre la señal (d); aria-labels + design tokens; adopción verify-only de URLs de endpoint en `image` | 📋 PLANNED |
| `PAIML-POLE-ANALYST-075` | Sanitización de display args en tool chips (sin rutas `/data/…`: caso chip `crop` de TOOL-06-SUB); helper compartido + specs | 📋 PLANNED |

## Tasks

1. **Error bubble/chip** — branchear sobre la señal de error del `agent_reply`; estilo de error
   Stitch con design tokens (nunca el chip `Completed`); el turno fallido queda en historial
   como error.
2. **Retry affordance** — reenvía el mismo mensaje vía `ChatbotService.sendMessage` (composer
   path, deshabilitado en Thinking/Working).
3. **A11y** — aria-labels WCAG 2.1 AA (`aria-label="chat error"`, `aria-live` según convenciones
   del chat-pane); sin leaks (`takeUntilDestroyed`).
4. **Image URLs** — verificar que el renderer `image` carga el `src` URL del endpoint (auth/proxy
   vía `ng serve` si hace falta); tocar el renderer solo si una asunción de container-path lo
   rompe; sin strings `/data/` en FE.
5. **Unit tests** — specs de error bubble/chip + estados de retry + `image` con URL; ≥ 80%
   cobertura; asserts de aria-labels y clases de design tokens.
6. **Tool-chip sanitization (075)** — helper compartido que elimina rutas absolutas
   (`/data/…`) de los display args de todos los tool chips (caso `crop` TOOL-06-SUB);
   specs de sanitización; sin cambios de comportamiento de chips.

## Acceptance

- Un turno ABANDONED/error rinde error bubble/chip + retry (nunca `Completed` + fallback).
- Retry reenvía por el composer path; deshabilitado en Thinking/Working.
- Sin subscription leaks; `npx ng test --watch=false` verde, `lint` limpio, `build` typecheck OK.
- Los bloques `image` con URL de endpoint cargan (verify-only si no hubo cambio).
- Los tool chips no muestran rutas de servidor (075: sin strings `/data/` en el chat pane).

## Dependencies

- **Blocks:** None.
- **Blocked By:** `pole_api` Phase 29 (`PAIML-POLE-API-093` — señal (d) + URLs (a); el FE
  desarrolla contra ese contrato con mock/stub hasta el E2E).
