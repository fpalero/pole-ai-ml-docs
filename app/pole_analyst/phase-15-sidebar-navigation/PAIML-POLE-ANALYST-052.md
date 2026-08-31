# PAIML-POLE-ANALYST-052 — Design Token Migration to Stitch Teal Palette

> **Phase:** 15 — Sidebar Navigation · **State:** 📋 PLANNED

## Objective

Update the CSS custom properties in `styles.scss` to match the Stitch "Kinetic Precision"
design system (teal primary #00685f, light surfaces #f8f9ff). Add sidebar-specific tokens.

## Scope

### Files to modify

- `app/pole_analyst/src/styles.scss` — update `:root` CSS custom properties

### Token changes

Replace the current indigo/green palette with the Stitch teal palette:

```scss
:root {
  /* Surfaces — Stitch */
  --background: #f8f9ff;
  --surface: #f8f9ff;
  --surface-container: #e6eeff;
  --surface-container-low: #eff4ff;
  --surface-container-high: #dee9fc;
  --surface-container-highest: #d9e3f6;

  /* Text — Stitch */
  --on-surface: #121c2a;
  --on-surface-variant: #3d4947;

  /* Borders — Stitch */
  --outline: #6d7a77;
  --outline-variant: #bcc9c6;

  /* Primary (teal) — Stitch */
  --primary: #00685f;
  --on-primary: #ffffff;
  --primary-container: #008378;
  --on-primary-container: #f4fffc;

  /* Secondary (gray) — Stitch */
  --secondary: #55615f;
  --on-secondary: #ffffff;
  --secondary-container: #d8e5e2;
  --on-secondary-container: #5b6765;

  /* Tertiary (brown) — Stitch */
  --tertiary: #924628;
  --on-tertiary: #ffffff;
  --tertiary-container: #b05e3d;
  --on-tertiary-container: #fffbff;

  /* Error — Stitch */
  --error: #ba1a1a;
  --on-error: #ffffff;
  --error-container: #ffdad6;
  --on-error-container: #93000a;

  /* Sidebar */
  --sidebar-width: 256px;
  --sidebar-bg: var(--surface-container-low);
  --sidebar-border: var(--outline-variant);

  /* Spacing (unchanged) */
  --sp-1: 4px;
  --sp-2: 8px;
  --sp-3: 12px;
  --sp-4: 16px;
  --sp-5: 24px;
  --sp-6: 32px;
  --sp-8: 48px;
  --sp-10: 64px;
  --sp-pane: 24px;
  --sp-gutter: 12px;

  /* Radii (unchanged) */
  --br-sm: 8px;
  --br-md: 12px;
  --br-full: 9999px;

  /* Shell layout */
  --top-bar-height: 56px;
  --pane-chat-width: 40%;
  --pane-tools-width: 60%;
  --pane-divider-width: 1px;
}
```

## Acceptance Criteria

1. All CSS tokens updated to Stitch palette values
2. `--sidebar-width` and `--sidebar-bg` tokens added
3. No visual regressions in existing components (tokens are semantic, components use `var()`)
4. `npx ng build` succeeds (typecheck)
5. All existing unit tests pass

## Testing

```bash
cd app/pole_analyst
npx ng build                    # typecheck
npx ng test --watch=false       # unit tests
```
