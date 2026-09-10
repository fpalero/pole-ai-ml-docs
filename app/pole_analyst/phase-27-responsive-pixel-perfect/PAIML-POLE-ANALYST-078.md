# Ticket: PAIML-POLE-ANALYST-078

## Title
[Responsive] Pixel-perfect Stitch Pole AI Coach (LIGHT only, login excluido) + ajuste de tests afectados

## Description
Fase 27 — ver [PLAN_PHASE_27](../plan/PLAN_PHASE_27.md). Aplicar el diseño
responsive Stitch `Pole AI Coach` (`projects/4315784734923719370`, rev
2026-09-09) pixel-perfect en `pole_analyst`, **un solo ticket** (scope estrecho
confirmado por PO). Solo `pole_analyst`; `pole_fe` fuera.

- Design system: **Kinetic Precision v2 LIGHT** (Inter, primary `#00685f`,
  surfaces `#f8f9ff/#ffffff/#eff4ff/#e6eeff`, 8px grid, `rounded-xl 24px` cards,
  tab underline 3px primary, pill chips, chat bubbles mint `#F0FDFA` derecha /
  off-white izquierda). El sistema oscuro `Galactic Stitch` se ignora.
- **Mobile dashboard = reflow del dashboard actual** (grupo colapsable
  `Dashboard ▾` → `/chat`, `tools:videos`, `tools:history` según fases 15/18).
  Sin ruta nueva, sin endpoint nuevo.
- **Login excluido (opción A):** `Login - Dual Authentication` +
  `Login - Mobile Responsive` fuera — login Keycloak + temp-access ya
  implementado y funcionando (vive en `pole-ai-ml-infra`).

FE-only: cero cambios backend. Endpoints reusados tal cual: `POST /videos`,
`GET /videos`, `GET /videos/summary`, `GET/ PATCH /videos/{id}`,
`PUT /videos/{id}/phase-frames`, `GET .../histogram|summary|metric-deltas|pose|pose/frames|coach-insights|coach-summary|landmarks|pose-analysis`,
`POST .../coach-plan|.../analyze (202)`, `GET/PUT /athlete-profile`,
WS `/ws/analyst-chat`, media con `?token=`.

## Screens (10, login excluido)

Desktop: Enhanced Pose Gallery, Multimodal Answer Card, Metrics+Chart,
Class-Name Modal, Phases Modal.
Mobile (390px): Dashboard (reflow), Video Library, Analysis Details,
AI Coach Chat, Multimodal Response Card.

## What to Do (Implementation Steps)
- [ ] Responsive shell: breakpoints `390/768/1280`; sidebar 256px desktop →
  header fijo `h-56px` + bottom-nav móvil; Bento 70/30 → single-column stack;
  pane padding 16–24px, gutters 12px, cero scroll-X a 390px.
- [ ] Pixel-perfect LIGHT: tokens exactos (colores/tipografía/radios/elevación
  `surface-bright` + cards `#ffffff` con borde 1px `outline-variant` +
  `shadow-sm` solo en flotantes); verificar `tokens.ts` vs Stitch v2 y
  corregir drift sin hardcodear en componentes.
- [ ] Paridad por screen (10): sidebar/header, dashboard reflow, library,
  detail (Summary/Histogram/Pose/Plan), pose gallery multi-frame, metric modal,
  coach answer card desktop+móvil, chat móvil, modales de clase/fases.
- [ ] **Ajustar TODOS los tests afectados por el responsive:** specs unit que
  rompan (selectores sidebar/header/bottom-nav, snapshots) + e2e Playwright
  (incl. viewport 390px: `sidebar-navigation`, `responsive`, history/tabs/chat
  specs y `coach-150q` si se ve afectado). Cobertura ≥ 80% en lo tocado.
- [ ] Checks: `npx ng test --watch=false` verde, `npx ng lint` limpio,
  `npx ng build` typecheck OK, Playwright verde (desktop + 390px).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Las 10 screens igualan Stitch LIGHT en 390/768/1280 (screenshot vs
  Stitch; cero scroll horizontal a 390px).
- [ ] Dashboard móvil = mismo contenido/navegación, solo reflow (sin rutas ni
  endpoints nuevos).
- [ ] Login intacto, sin cambios.
- [ ] Todos los tests afectados actualizados y verdes (unit + e2e desktop/móvil).
- [ ] `ng test` verde, `lint` limpio, `build` OK.
- [ ] Zero backend change.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`
- [ ] `npx ng lint`
- [ ] `npx ng build`
- [ ] `npx playwright test` (incl. viewport móvil 390px)

## Dependencies
- **Blocks**: None.
- **Blocked By**: None. FE-only; base shell fases 15/18/20; backend
  `analysis` + `/ws/analyst-chat` + `?token=` ya existen.

## Estimated Effort
- [M]
