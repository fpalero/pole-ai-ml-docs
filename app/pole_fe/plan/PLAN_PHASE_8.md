# Fase 8 — Integration, E2E & Polish — ✅ E2E DONE (Playwright)

> Plan maestro: [PLAN.md](PLAN.md)

## Tareas

- [x] Cross-page integration (detail → editor → studio → registry), error-state polish, toast queue.
- [x] Playwright E2E suite E2E-1..E2E-20 (Workflows A/B/C, editor, registry, jobs, errors, responsive) — spec en `docs/app/pole_fe/e2e-test-plan.md`, impl en `app/pole_fe/e2e/`, run via `pixi run fe-e2e`.
- [ ] WCAG 2.1 AA audit; bundle analysis + code-splitting validation; virtual scroll para listas grandes; lazy image loading.
- [ ] QA checklist (los 33 endpoints conectados, componentes con estado empty/loading/error/success, keyboard nav, `aria-live` job announcements).

## Criterios de aceptación

- [x] E2E Playwright verde (E2E-1..20).
- [ ] Pendiente: audit WCAG, bundle, virtual scroll, QA checklist completo.