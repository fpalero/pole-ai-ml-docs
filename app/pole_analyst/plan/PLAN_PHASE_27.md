# Fase 27 — Responsive pixel-perfect (Stitch Pole AI Coach, LIGHT only) — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Backend requerido: ninguno (FE-only; todos los
> datos ya los proveen los endpoints `analysis` + WS `/ws/analyst-chat` + `?token=` media auth).
> Diseño: Stitch `Pole AI Coach` (`projects/4315784734923719370`, rev 2026-09-09) —
> design system **Kinetic Precision v2 LIGHT** (Inter, primary `#00685f`, surfaces
> `#f8f9ff/#ffffff/#eff4ff/#e6eeff`, 8px grid, `rounded-xl`). El sistema oscuro
> `Galactic Stitch` se ignora. **Login excluido** (opción A confirmada por PO:
> login Keycloak + temp-access ya implementado y funcionando, vive en
> `pole-ai-ml-infra`, no en `pole_analyst`).

## Contexto

La app ya implementa tokens Kinetic en `src/app/design-tokens/tokens.ts` y shell
sidebar 256px + top-bar slim + split 40/60 (fases 15/18/20), pero no aplica el
responsive Stitch pixel-perfect: Bento 70/30 → single-column en móvil, header
fijo `h-56px` + bottom-nav en móvil, y las 5 parejas desktop/móvil con drift de
spacing/tipografía/radios. El "Dashboard móvil" es el **reflow responsive del
dashboard actual** (header del grupo colapsable `Dashboard ▾` → `/chat`, ver
fases 15/18) — NO es ruta nueva ni requiere agregación backend.

## Screens Stitch cubiertas (10, login excluido)

Desktop (12-col, gutters 24px, márgenes 32px):
- `Analysis Details - Enhanced Pose Gallery` (`ab6d9abf...`)
- `AI Coach - Multimodal Analysis Answer Card` (`e6a4363e...`)
- `Analysis Details - Metrics and Chart Integration` (`5622a324...`)
- `Video Library - Class Name Configuration Modal` (`c0851595...`)
- `Video Library - Phases Configuration Modal` (`96cfaee9...`)

Mobile (4-col, 390px, márgenes 16px):
- `Dashboard - Mobile` = reflow del dashboard actual (`a14f0e0f...`)
- `Video Library - Mobile` (`dfae8303...`)
- `Analysis Details - Mobile` (`d013b2d0...`)
- `AI Coach Chat - Mobile` (`8153376d...`)
- `AI Coach - Multimodal Analysis Response Card (Mobile)` (`ed50e9f9...`)

Explícitamente fuera: `Login - Dual Authentication` (`f1114f2f...`) +
`Login - Mobile Responsive` (`0aa9b4fafa...`).

## Tickets

| Ticket | Scope | Estado |
| :--- | :--- | :--- |
| `PAIML-POLE-ANALYST-078` | Responsive shell (breakpoints 390/768/1280, header/bottom-nav móvil, Bento→stack) + pixel-perfect de las 10 screens + ajuste de TODOS los tests afectados (unit + e2e) | 📋 PLANNED |

## Tasks

1. **Responsive shell** — breakpoints `390/768/1280`; sidebar 256px en desktop →
   header fijo `h-56px` + bottom-nav en móvil; Bento 70/30 → single-column stack;
   pane padding 16–24px, gutters 12px, sin scroll horizontal a 390px.
2. **Pixel-perfect** — aplicar tokens LIGHT exactos (teal `#00685f`, superficies,
   Inter h1 32/24 h2 24/20 body 16/18 label 14/12, radios `xl 24px / lg 16px /
   pill`, tab underline 3px primary, chat bubbles mint `#F0FDFA` dcha /
   off-white izqda); comparar screenshot-vs-Stitch por screen.
3. **Dashboard móvil = reflow** — sin ruta ni endpoint nuevos; el grupo
   colapsable `Dashboard ▾` y sus destinos (`/chat`, `tools:videos`,
   `tools:history`) se conservan, solo cambia layout.
4. **Tests afectados** — actualizar TODOS los specs/e2e que rompan con el
   responsive (selectores sidebar/header/bottom-nav, snapshots, specs
   `sidebar-navigation`, `responsive`, `coach-150q` si aplica); `ng test`
   ≥ 80% coverage, `lint` + `build` limpios, Playwright verde incl. viewport
   móvil 390px.

## Acceptance

- Las 10 screens igualan Stitch LIGHT pixel-perfect en 390/768/1280 (spot check
  screenshot vs Stitch, cero scroll-X a 390px).
- Dashboard móvil es reflow (misma navegación, sin endpoints nuevos).
- Login intacto (sin cambios).
- `npx ng test --watch=false` verde, `npx ng lint` limpio, `npx ng build` OK,
  Playwright e2e verde (desktop + 390px).
- Cero cambios backend.

## Dependencies

- **Blocks:** None.
- **Blocked By:** None (FE-only; endpoints `analysis` + `/ws/analyst-chat` +
  `?token=` ya existen; fases 15/18/20 como base del shell).
