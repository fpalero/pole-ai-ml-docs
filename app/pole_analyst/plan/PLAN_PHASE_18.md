# Fase 18 — Stitch sidebar submenu (Dashboard colapsable) — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Diseño: Stitch "Pole AI Coach" — side menu con grupo
> colapsable `Dashboard ▾` (detectado en la revisión de paridad 2026-08-23, tras Phase 17)

## Contexto

Phase 17 aligned sidebar *items* (Coach added → chat pane, Settings removed) but the Stitch design
structures the menu as a collapsible `Dashboard ▾` group with the entries nested beneath it. The
app renders a flat list — structural gap confirmed by PO on 2026-08-23.

## Alcance

Single ticket `PAIML-POLE-ANALYST-063`: collapsible group in `SidebarComponent` (chevron toggle,
`aria-expanded`, indented children, default expanded), navigation targets unchanged, specs + E2E
selectors updated.

## Quality Gates

- **Unit Tests:** `npx ng test --watch=false` — suite green.
- **E2E:** `sidebar-navigation.spec.ts` green after selector updates.
- **Additional Checks:** `ng build` clean; keyboard operability.

## Dependencies

- None (builds on Phase 17's merged sidebar).
