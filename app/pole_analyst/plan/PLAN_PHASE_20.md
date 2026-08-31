# Fase 20 — Sidebar Option B (solo menú lateral) — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Decisión PO 2026-08-24: navegación SOLO por el menú
> lateral; se elimina Coach y Upload del sidebar; la barra de pestañas de la página de vídeos
> queda eliminada (se ratifica 4d9666c).

## Contexto

Dos direcciones de diseño convivían en main (Stitch refresh fases 12–14 con tab bar vs. el enfoque
flat del agente paralelo). El PO eligió **Option B**: solo menú lateral. El chat sigue siempre
visible en el panel izquierdo; la subida de vídeos vive en el panel Library.

## Tickets

| Ticket | Scope | Estado |
| :--- | :--- | :--- |
| `PAIML-POLE-ANALYST-068` | Sidebar: quitar Coach + Upload; queda Dashboard ▾ / Library / Analysis | 📋 PLANNED |
| `PAIML-POLE-ANALYST-069` | Realineación E2E Option B (retirar expectativas de tab bar; triage 18 fallos) | 📋 PLANNED |

## Quality Gates

- Unit suite green; build clean; **full analyst E2E green** en config aislada (puertos/DBs
  desechables documentados).
