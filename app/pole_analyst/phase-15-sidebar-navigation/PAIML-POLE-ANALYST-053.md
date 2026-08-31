# PAIML-POLE-ANALYST-053 — Create SidebarComponent

> **Phase:** 15 — Sidebar Navigation · **State:** 📋 PLANNED

## Objective

Create the `SidebarComponent` in `shared/components/sidebar/` matching the Stitch "Pole AI
Coach" sidebar design. Standalone, inline template/styles, Angular v20 conventions.

## Scope

### Files to create

- `app/pole_analyst/src/app/shared/components/sidebar/sidebar.component.ts`

### Design spec (from Stitch)

**Layout:**
```
┌─────────────────────────┐
│ [icon] Pole AI Coach    │
│        AI video analysis│
├─────────────────────────┤
│ [ Upload Video button ] │
├─────────────────────────┤
│ ▸ Dashboard             │
│ ▸ Library               │
│ ▸ Analysis              │
├─────────────────────────┤
│ (spacer mt-auto)        │
│ ▸ Settings              │
└─────────────────────────┘
```

**Dimensions:** 256px wide, full height, fixed left, `bg-surface-container-low`, right border.

**Nav items:**

| Label | Icon | Route | Outlet |
| :--- | :--- | :--- | :--- |
| Dashboard | `dashboard` | `/chat` | primary |
| Library | `video_library` | `/videos` | tools |
| Analysis | `analytics` | `/history` | tools |
| Settings | `settings` | — | — (disabled) |

**States:**
- Active: `bg-primary-container text-on-primary-container font-semibold rounded-lg` + filled icon
- Inactive: `text-on-surface-variant hover:bg-surface-variant` + outline icon
- Disabled (Settings): `opacity-50 cursor-not-allowed`

**Upload button:** `bg-primary text-on-primary rounded-lg` with `upload` icon, full width.

**Brand block:** Material icon `fitness_center` in `bg-primary-container` rounded square +
"Pole AI Coach" title + "AI video analysis for pole athletes" subtitle.

**Accessibility:**
- `<nav aria-label="Main navigation">`
- Active item: `aria-current="page"`
- Keyboard: tab through items, Enter/Space to activate
- Focus visible: `2px solid var(--primary)` outline

### Implementation notes

- Use `Router` and `ActivatedRoute` to determine active state
- Use `RouterLink` and `RouterLinkActive` for navigation
- `RouterLinkActive` can detect which nav item matches current route
- For the tools outlet, detect active state by checking if URL contains the route path
- Settings item: `[disabled]="true"` with tooltip "Coming soon"

## Acceptance Criteria

1. Sidebar renders with brand block, upload button, 4 nav items
2. Active item highlighted based on current route
3. Clicking nav items navigates to correct routes/outlets
4. Settings item is disabled with "Coming soon" tooltip
5. Upload button emits an event (parent handles upload flow)
6. Keyboard navigation works (Tab, Enter, Space)
7. WCAG 2.1 AA (ARIA landmarks, focus management)
8. Unit tests pass for component rendering and navigation

## Testing

```bash
cd app/pole_analyst
npx ng test --watch=false       # unit tests
```
