# Performance + Loading Time — Next.js App Router

> Reference spec for scaffolding loading states, Suspense boundaries, skeleton components, and performance patterns.
> Status: Approved

## Architecture

Four layers:
1. **Route-level loading** — `loading.tsx` files for instant shell rendering
2. **Component-level Suspense** — granular boundaries for streaming RSC
3. **Skeleton system** — consistent placeholder components
4. **Performance rules** — bundle, fonts, images, dynamic imports

## Route-level loading

Every route that fetches data should have a `loading.tsx` sibling:

```
app/
  dashboard/
    page.tsx          ← fetches data
    loading.tsx       ← shown instantly while page.tsx suspends
  blog/
    [slug]/
      page.tsx
      loading.tsx
```

`loading.tsx` wraps the page skeleton. Next.js streams the shell immediately then hydrates when data is ready.

## Component-level Suspense

For granular streaming (parts of a page load independently):

```tsx
<Suspense fallback={<CardSkeleton />}>
  <RecentOrders />   {/* async Server Component */}
</Suspense>
```

Rules:
- Every async Server Component that does IO should be wrapped in Suspense
- Use specific skeleton matching the real content dimensions
- Never use a generic spinner as fallback — it causes layout shift

## Skeleton system

Skeletons live in `components/ui/skeletons/`. Each skeleton:
- Matches the real component's layout exactly (same padding, font sizes, line counts)
- Uses `animate-pulse` (Tailwind) not custom CSS
- Accepts className for size overrides
- Has `aria-busy="true"` on the container

Standard set: `CardSkeleton`, `TableSkeleton`, `TextSkeleton`, `AvatarSkeleton`, `PageHeaderSkeleton`

## Performance rules

### Images
- Always `next/image` with explicit dimensions or `fill`
- LCP images: add `priority` prop
- Never raw `<img>` in Next.js projects

### Fonts
- Always `next/font/google` with `display: 'swap'`
- Never `@import` in CSS
- Apply via CSS variable on `<html>`

### Dynamic imports
- Large Client Components: wrap with `dynamic(() => import(...), { ssr: false })`
- Rich text editors, charts, maps, heavy UI libs: always dynamic

### Bundle analysis
```bash
npm install -D @next/bundle-analyzer
```
```ts
// next.config.ts — wrap config with analyzer
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})
export default withBundleAnalyzer(nextConfig)
```
Run: `ANALYZE=true npm run build`

## File map

| File | Responsibility |
|---|---|
| `app/dashboard/loading.tsx` | Route-level skeleton for dashboard |
| `components/ui/skeletons/index.ts` | Barrel export for all skeletons |
| `components/ui/skeletons/CardSkeleton.tsx` | Card placeholder |
| `components/ui/skeletons/TableSkeleton.tsx` | Table placeholder |
| `components/ui/skeletons/TextSkeleton.tsx` | Text block placeholder |
| `components/ui/skeletons/AvatarSkeleton.tsx` | Avatar/icon placeholder |
| `components/ui/skeletons/PageHeaderSkeleton.tsx` | Page title + subtitle placeholder |
| `lib/perf/dynamic.ts` | Typed dynamic import helpers |
