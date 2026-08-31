# Fase 15 — Stitch Design: Sidebar Navigation — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md) · Feature: Stitch "Pole AI Coach" sidebar navigation — FE `pole_analyst`

## Contexto

The `pole_analyst` Angular FE is being updated to match the Stitch "Pole AI Coach" design
(`projects/4315784734923719370`). This phase replaces the current top-bar-only navigation with a
fixed left sidebar matching the Stitch design, plus a slim top bar for brand/actions.

**Stitch design source:** 5 screens from the Pole AI Coach project — all show a consistent
256px sidebar with nav items (Dashboard, Library, Analysis, Settings) and an Upload Video button.

**Key decisions (confirmed by PO):**
- Match Stitch light theme (teal #0d9488 primary, #f8f9ff background)
- Dashboard maps to `/chat` (existing)
- Library maps to `tools:videos` (existing)
- Analysis maps to `tools:history` (existing)
- Settings: include nav item but skip route (placeholder)
- Include Upload Video button in sidebar
- Layout: sidebar (256px) + slim top bar + two panes (chat + tools)

## Alcance

### 1. Design token migration to Stitch teal palette

Update `styles.scss` CSS custom properties to match the Stitch "Kinetic Precision" design system:

| Token | Current | Stitch |
| :--- | :--- | :--- |
| `--primary` | `#4F46E5` (indigo) | `#00685f` (teal) |
| `--on-primary` | `#FFFFFF` | `#FFFFFF` |
| `--primary-container` | `#E0E7FF` | `#008378` |
| `--on-primary-container` | `#312E81` | `#f4fffc` |
| `--secondary` | `#16A34A` (green) | `#55615f` (gray) |
| `--on-secondary` | `#FFFFFF` | `#FFFFFF` |
| `--secondary-container` | `#DCFCE7` | `#d8e5e2` |
| `--on-secondary-container` | `#14532D` | `#5b6765` |
| `--background` | `#FAFBFC` | `#f8f9ff` |
| `--surface` | `#FFFFFF` | `#f8f9ff` |
| `--surface-container` | `#FAFBFC` | `#e6eeff` |
| `--surface-container-high` | `#F3F4F6` | `#dee9fc` |
| `--on-surface` | `#1F2937` | `#121c2a` |
| `--on-surface-variant` | `#4B5563` | `#3d4947` |
| `--outline` | `#D1D5DB` | `#6d7a77` |
| `--outline-variant` | `#E5E7EB` | `#bcc9c6` |
| `--error` | `#DC2626` | `#ba1a1a` |
| `--error-container` | `#FEE2E2` | `#ffdad6` |
| `--tertiary` | `#F59E0B` | `#924628` |
| `--tertiary-container` | `#FEF3C7` | `#b05e3d` |

Add new tokens for sidebar:
- `--sidebar-width: 256px`
- `--sidebar-bg: var(--surface-container-low)`
- `--sidebar-border: var(--outline-variant)`

### 2. SidebarComponent (shared)

New component `shared/components/sidebar/sidebar.component.ts` — inline template/styles,
standalone, Angular v20 conventions.

**Structure:**
```
┌─────────────────────────┐
│ [logo] Pole AI Coach    │
│        tagline           │
├─────────────────────────┤
│ [Upload Video button]   │
├─────────────────────────┤
│ ▸ Dashboard             │
│ ▸ Library               │
│ ▸ Analysis              │
├─────────────────────────┤
│ (spacer mt-auto)        │
│ ▸ Settings              │
└─────────────────────────┘
```

**Nav items:**
| Label | Icon | Route | Outlet |
| :--- | :--- | :--- | :--- |
| Dashboard | `dashboard` | `/chat` | primary |
| Library | `video_library` | `/videos` | tools |
| Analysis | `analytics` | `/history` | tools |
| Settings | `settings` | — | — (disabled) |

**Active state:** `bg-primary-container text-on-primary-container font-semibold rounded-lg`
+ filled icon (`font-variation-settings: 'FILL' 1`)

**Inactive state:** `text-on-surface-variant hover:bg-surface-variant` + outline icon

**Upload button:** `bg-primary text-on-primary rounded-lg` with `upload` icon, positioned above nav items.

**Accessibility:** WAI-ARIA navigation landmark, `aria-label="Main navigation"`, active item
marked with `aria-current="page"`, keyboard navigable.

### 3. AppComponent layout refactor

Update `app.ts` to include the sidebar and slim top bar:

**New layout:**
```
┌──────────┬────────────────────────────────────┐
│          │ Top Bar (56px, slim)                │
│ Sidebar  ├────────────────┬───────────────────┤
│ (256px)  │ Chat (40%)     │ Tools (60%)       │
│          │                │                   │
│          │                │                   │
└──────────┴────────────────┴───────────────────┘
```

- Sidebar: fixed left, 256px wide, full height
- Top bar: spans remaining width (calc(100% - 256px)), 56px height
- Panes: fill remaining space below top bar
- Remove brand block from top bar (brand moves to sidebar header)
- Keep settings/avatar actions in top bar

### 4. Router outlet changes

Current routes use a named `tools` outlet. The sidebar navigates both outlets:
- Dashboard → primary outlet (`/chat`)
- Library → tools outlet (`tools:videos`)
- Analysis → tools outlet (`tools:history`)

The `AppComponent.ngOnInit` logic that defaults the tools outlet to `/videos` remains unchanged.

### 5. VideosLibraryPage TabBar removal

Remove the `TabBar` from `VideosLibraryPage` since navigation is now handled by the sidebar.
The page will only show the `VideosLibraryPane` directly (no tab switching needed — Library is
a dedicated page, not a tab container).

The `analysis-history` tab is removed from `VideosLibraryPage` since Analysis is now a
top-level sidebar item with its own route.

## Ticket Breakdown

| Ticket | Title | Est. |
| :--- | :--- | :--- |
| PAIML-POLE-ANALYST-052 | Design token migration to Stitch teal palette | S |
| PAIML-POLE-ANALYST-053 | Create SidebarComponent | M |
| PAIML-POLE-ANALYST-054 | Refactor AppComponent layout (sidebar + slim top bar) | M |
| PAIML-POLE-ANALYST-055 | Wire sidebar navigation to routes + remove TabBar | M |
| PAIML-POLE-ANALYST-056 | Unit tests for sidebar + updated app shell | M |
| PAIML-POLE-ANALYST-057 | Playwright e2e tests for sidebar navigation | S |

## Acceptance Criteria

1. Sidebar renders at 256px fixed-left with brand block, upload button, 4 nav items, settings
2. Active nav item highlights with `bg-primary-container` + filled icon
3. Clicking Dashboard navigates to `/chat` (primary outlet)
4. Clicking Library navigates to `tools:videos`
5. Clicking Analysis navigates to `tools:history`
6. Settings item is visible but disabled (no route)
7. Upload Video button is visible and clickable (triggers existing upload flow)
8. Top bar is slim (56px) and spans remaining width after sidebar
9. Two-pane layout (chat + tools) preserved below top bar
10. All existing unit tests pass
11. New sidebar tests pass
12. Playwright e2e tests pass for sidebar navigation
13. WCAG 2.1 AA compliance (keyboard nav, ARIA landmarks, focus management)
