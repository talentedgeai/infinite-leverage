---
name: scaffold-performance
description: >-
  Stamps loading states, Suspense boundaries, skeleton components, and performance
  best practices (dynamic imports, LCP images, fonts, bundle analysis) into the current
  Next.js App Router project. Invoke when a user asks to "add loading states",
  "scaffold skeletons", "improve loading time", "add Suspense", "fix CLS", or similar.
---

# Scaffold: Performance + Loading States

Stamps loading UX infrastructure and performance patterns into the current project.

## Before you start

Ask:
- **Which routes need loading states?** (e.g. `/dashboard`, `/orders` — list them; default: `/dashboard`)
- **How many columns in your main data table?** (default: 4)
- **How many stat cards on dashboard?** (default: 4)

Note as `$ROUTES`, `$TABLE_COLUMNS`, `$STAT_COUNT`.

---

## Step 1 — Skeleton component system

Create `components/ui/skeletons/` with these components:

| Component | Use for |
|---|---|
| `CardSkeleton` | stat cards, summary boxes |
| `TableSkeleton` | data tables (accepts `rows`, `columns` props) |
| `TextSkeleton` | paragraphs, descriptions |
| `AvatarSkeleton` | user avatars with optional name text |
| `PageHeaderSkeleton` | page title + subtitle |

All skeletons:
- Use `animate-pulse` (Tailwind)
- Have `aria-busy="true"` and `aria-label="Loading"`
- Accept `className` for size overrides

Export all from `components/ui/skeletons/index.ts`.

See full implementations in `templates/project-scaffold/website/components/ui/skeletons/`.

---

## Step 2 — Route-level loading files

For each route in `$ROUTES`, create `app/<route>/loading.tsx`:

```tsx
// app/$ROUTE/loading.tsx
import { PageHeaderSkeleton } from '@/components/ui/skeletons'
import { CardSkeleton } from '@/components/ui/skeletons'
import { TableSkeleton } from '@/components/ui/skeletons'

export default function Loading() {
  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeaderSkeleton />
      <div className="grid grid-cols-$STAT_COUNT gap-4">
        {Array.from({ length: $STAT_COUNT }).map((_, i) => (
          <CardSkeleton key={i} lines={2} />
        ))}
      </div>
      <TableSkeleton rows={8} columns={$TABLE_COLUMNS} />
    </div>
  )
}
```

**Rule**: every `page.tsx` that calls `await` at the top level needs a sibling `loading.tsx`.

---

## Step 3 — Granular Suspense for parallel loading

In pages with multiple independent data sections, wrap each section:

```tsx
import { Suspense } from 'react'
import { CardSkeleton } from '@/components/ui/skeletons'

// Each Suspense boundary fetches in parallel — faster than sequential awaits
<Suspense fallback={<CardSkeleton />}>
  <MetricA />   {/* async Server Component */}
</Suspense>
<Suspense fallback={<CardSkeleton />}>
  <MetricB />
</Suspense>
```

**Rule**: do NOT await multiple data sources sequentially in one Server Component. Use Suspense boundaries to fan out fetches.

---

## Step 4 — Dynamic imports for heavy components

Create `lib/perf/dynamic.ts`:
```ts
import dynamic from 'next/dynamic'
export function clientOnly(loader, options?) {
  return dynamic(loader, { ssr: false, loading: options?.loading })
}
export function lazyLoad(loader, options?) {
  return dynamic(loader, { ssr: options?.ssr ?? true, loading: options?.loading })
}
```

Apply immediately to:
- Rich text editors: `clientOnly(() => import('@/components/editor/MDXEditorFull'))`
- Charts/maps: `clientOnly(() => import('@/components/Chart'))`
- Any component with `'use client'` that imports a library > 50kB

---

## Step 5 — Performance rules (enforce on all pages)

Apply these checks to every page during development:

**Images**: replace any `<img>` with `next/image`. Add `priority` to the largest above-the-fold image.

**Fonts**: if `@import` is in any CSS file, move it to `lib/seo/fonts.ts` with `next/font`.

**Sequential awaits**: if a Server Component does:
```ts
const a = await fetchA()
const b = await fetchB()
```
Replace with `Promise.all` or separate Suspense boundaries.

**Large imports**: if any `import` resolves to a bundle > 100kB (check with ANALYZE), wrap with `clientOnly`.

---

## Step 6 — Bundle analyzer (optional but recommended)

```bash
npm install -D @next/bundle-analyzer
```

```ts
// next.config.ts
import withBundleAnalyzer from '@next/bundle-analyzer'
const analyzer = withBundleAnalyzer({ enabled: process.env.ANALYZE === 'true' })
export default analyzer(nextConfig)
```

Run: `ANALYZE=true npm run build` — opens treemap in browser.

---

## Post-scaffold TODOs

| File | TODO |
|---|---|
| `app/$ROUTE/loading.tsx` | Match skeleton layout to your real page exactly (same grid, column count) |
| `components/ui/skeletons/CardSkeleton.tsx` | Adjust height and line count to match real cards |
| `components/ui/skeletons/TableSkeleton.tsx` | Set default `columns` to your table column count |
| `lib/perf/dynamic.ts` | Apply `clientOnly` to all heavy Client Components in the project |

---

## Core rules (do not deviate)

- **Never use a spinner as a Suspense fallback** — it causes layout shift; use a skeleton matching the real dimensions
- **Never skip `loading.tsx`** on routes that fetch data — the page will blank during navigation
- **Never `await` sequentially** in a Server Component when data is independent — use `Promise.all` or Suspense
- **Never import heavy libs without dynamic import** — editors, charts, maps, date pickers

Reference: `templates/project-scaffold/website/` in infiniteleverage-8-agents-template.
