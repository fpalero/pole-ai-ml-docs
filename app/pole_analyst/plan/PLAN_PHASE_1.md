# Fase 1 — Foundation & App Shell — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md)

## Tareas

- [ ] Infra Angular 22 scaffold (esbuild, Tailwind, `@angular/build:unit-test` vitest runner), light-theme design tokens de `fe_design.md`, two-pane split layout + slim top bar.
- [ ] Infra `ApiClient` + error interceptor (`{detail}` envelope → typed error), `ng serve` proxy (`/api`, `/ws` → backend), lazy routes.
- [ ] Presentation `StatusChip`, `TabBar`, `Card`, `Badge`, `UploadDropzone` shared atoms.
- [ ] App `ChatState` model + reducer (Idle/Thinking/Working/Completed/Error).
- [ ] Test unit tests T1.x (layout, atoms, interceptor, state machine).

## Criterios de aceptación

- [ ] Scaffold con vitest; shell de dos panes; atoms compartidos; tests T1.x verdes.