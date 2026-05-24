---
name: scaffold-dashboard
description: >-
  Stamps a protected dashboard layout shell (sidebar nav, breadcrumbs, mobile drawer,
  auth guard) into the current Next.js + Supabase project. Invoke when a user asks to
  "scaffold dashboard", "add dashboard layout", or "add sidebar nav".
---

# Scaffold: Dashboard Layout

Stamps a production-ready protected dashboard shell into the current project in one pass.
Architecture: auth guard → Server Component layout → Client Component shell → Sidebar + MobileDrawer + Breadcrumbs.

## Before you start

1. Confirm the project uses **Next.js App Router** + **Supabase** (look for `app/` directory and `@supabase/ssr` imports).
2. Confirm `scaffold-auth` has already been applied — this skill requires `lib/auth/guards.ts` and `lib/auth/actions.ts` to exist.
3. Ask these customisation questions — state the default for each:

   - **Dashboard route path?** (default: `/dashboard`)
   - **Auth guards already set up?** (default: yes — requires scaffold-auth to be applied first)
   - **Supabase server client import path?** (default: `@/lib/supabase/server`)

4. Note the answers as `$DASHBOARD_PATH`, `$AUTH_GUARD`, `$SUPABASE_PATH`.

---

## Step 1 — Nav config

Create `lib/dashboard/nav-config.ts`:

```ts
export interface NavItem {
  label: string
  href: string
  icon?: string   // Lucide icon name as string — TODO: replace with actual import
  children?: NavItem[]
}

export const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: 'LayoutDashboard' },
  { label: 'Settings', href: '/dashboard/settings', icon: 'Settings' },
  // TODO: add your project's nav items here
]
```

---

## Step 2 — Layout (Server Component)

Create `app/$DASHBOARD_PATH/layout.tsx`:

```tsx
import { requireAuth } from '@/lib/auth/guards'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'

export default async function Layout({ children }: { children: React.ReactNode }) {
  const user = await requireAuth()   // redirects to /login if unauthenticated
  return <DashboardLayout user={user}>{children}</DashboardLayout>
}
```

This is a **Server Component** — no `'use client'`. Auth check happens server-side before any HTML is streamed.

---

## Step 3 — DashboardLayout (Client Component)

Create `components/dashboard/DashboardLayout.tsx`:

- `'use client'`
- Flex layout: `<Sidebar>` (hidden on mobile, `lg:flex hidden`) + `<main className="flex-1 overflow-auto">`
- Mobile: `<Header>` at top with hamburger → toggles `<MobileDrawer>`
- Manages `mobileOpen: boolean` state, passes `onToggle` to `<Header>` and `open/onClose` to `<MobileDrawer>`
- Accepts `user: { id: string; email: string }` prop, passes to `<Sidebar>`

---

## Step 4 — Sidebar (Client Component, desktop)

Create `components/dashboard/Sidebar.tsx`:

- `'use client'`
- `lg:flex hidden flex-col w-64 border-r bg-background`
- Logo slot at top: `{/* TODO: replace with project logo */}`
- Maps `NAV_ITEMS` to `<SidebarItem>` components
- User section at bottom: avatar initials + email display + logout `<button>` that calls `logout()` server action from `@/lib/auth/actions`

---

## Step 5 — SidebarItem (Client Component)

Create `components/dashboard/SidebarItem.tsx`:

- `'use client'`
- Props: `{ href: string; label: string; icon?: string }`
- Active state: compare `usePathname()` with `href`
- `aria-current="page"` when active
- Icon rendered as text placeholder: `<span aria-hidden="true">{icon}</span> {/* TODO: use Lucide icon */}`
- Uses `<Link>` from `next/link`

---

## Step 6 — MobileDrawer (Client Component)

Create `components/dashboard/MobileDrawer.tsx`:

- `'use client'`
- Props: `{ open: boolean; onClose: () => void }`
- `fixed inset-0 z-50` — backdrop + slide-in panel from left
- Same `NAV_ITEMS` mapped to `<SidebarItem>` components
- Closes on nav item click (wrap nav in `<div onClick={onClose}>`) and on backdrop click
- Focus trap: `useEffect` on `open` → `querySelectorAll` for focusable elements → focus first on open
- ESC key: `useEffect` adds `keydown` listener, calls `onClose` on `Escape`
- Returns `null` when `!open` (unmounts fully)

---

## Step 7 — Breadcrumbs (Client Component)

Create `components/dashboard/Breadcrumbs.tsx`:

- `'use client'`
- Auto-generates from `usePathname()`: split on `/`, filter empty, map segments to labels
- Capitalise each segment label: `segment.charAt(0).toUpperCase() + segment.slice(1)`
- Each segment except the last is a `<Link>`, last is plain text (current page)
- Returns `null` if pathname is exactly `/dashboard` (root dashboard path)
- `<nav aria-label="Breadcrumb"><ol>` with `<li>` items and `/` separators

---

## Step 8 — Header (Client Component, mobile top bar)

Create `components/dashboard/Header.tsx`:

- `'use client'`
- Props: `{ onMobileMenuToggle: () => void; children?: React.ReactNode }`
- `lg:hidden flex items-center justify-between h-14 px-4 border-b bg-background`
- Hamburger `<button type="button" aria-label="Open menu">` → calls `onMobileMenuToggle`
- `<Breadcrumbs />` in the centre (or page title fallback)
- `{children}` slot on the right (for notifications bell etc.)

---

## Step 9 — Post-scaffold TODOs (leave as comments in the code)

| File | TODO |
|---|---|
| `lib/dashboard/nav-config.ts` | Replace placeholder nav items with your app's routes and Lucide icons |
| `components/dashboard/Sidebar.tsx` | Replace logo placeholder with project logo |
| `components/dashboard/DashboardLayout.tsx` | Replace Tailwind classes with project design system |
| `app/$DASHBOARD_PATH/layout.tsx` | If auth is not yet set up, run `/scaffold-auth` first |

---

## Step 10 — Verify

```bash
npx tsc --noEmit   # must pass with 0 errors before handing off
```

Reference implementation: `templates/project-scaffold/website/` in the infiniteleverage-8-agents-template repo.
