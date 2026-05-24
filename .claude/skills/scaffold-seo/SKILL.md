---
name: scaffold-seo
description: >-
  Stamps SEO metadata helpers, structured data (JSON-LD), sitemap, robots.txt,
  and performance best practices into the current Next.js App Router project.
  Invoke when a user asks to "add SEO", "scaffold metadata", "set up sitemap",
  "add structured data", "add Open Graph", or similar.
---

# Scaffold: SEO + Performance

Stamps production-ready SEO infrastructure into the current Next.js App Router project.

## Before you start

Ask these customisation questions:
- **Site name?** (e.g. "My SaaS App")
- **Site URL env var?** (default: `NEXT_PUBLIC_SITE_URL`)
- **Default OG image path?** (default: `/opengraph-image.png`)
- **Body font?** (default: Inter — any Google Font name works)
- **Display/heading font?** (default: same as body — skip `fontDisplay` if same)
- **Dynamic content types for sitemap?** (e.g. blog posts, products — default: none)

Note as `$SITE_NAME`, `$SITE_URL_VAR`, `$OG_IMAGE`, `$BODY_FONT`, `$DISPLAY_FONT`, `$DYNAMIC_ROUTES`.

---

## Step 1 — Create metadata helpers

### `lib/seo/metadata.ts`
- Export `BASE_URL = process.env.$SITE_URL_VAR ?? 'https://example.com'`
- Export `baseMetadata: Metadata` with title template `'%s | $SITE_NAME'`, description, OG defaults
- Export `buildMetadata(overrides)` that builds canonical URL, OG, Twitter Card

### `lib/seo/structured-data.ts`
- Export `websiteSchema()`, `organizationSchema()`, `articleSchema()`, `breadcrumbSchema()`
- Fill in `$SITE_NAME` and `$SITE_URL` in website and org schemas

### `components/seo/JsonLd.tsx`
```tsx
export function JsonLd({ schema }: { schema: Record<string, unknown> | Record<string, unknown>[] }) {
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />
}
```

---

## Step 2 — Add base metadata to layout

In `app/layout.tsx`, add:
```ts
import { baseMetadata } from '@/lib/seo/metadata'
import { websiteSchema, organizationSchema } from '@/lib/seo/structured-data'
import { JsonLd } from '@/components/seo/JsonLd'

export const metadata = baseMetadata

// Inside <body>:
// <JsonLd schema={[websiteSchema(), organizationSchema()]} />
```

---

## Step 3 — Sitemap + robots

### `app/sitemap.ts`
```ts
import type { MetadataRoute } from 'next'
import { BASE_URL } from '@/lib/seo/metadata'
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  return [
    { url: BASE_URL, lastModified: new Date(), changeFrequency: 'daily', priority: 1 },
    // TODO: add more static routes
    // TODO: add dynamic routes if $DYNAMIC_ROUTES is set
  ]
}
```

### `app/robots.ts`
```ts
export default function robots(): MetadataRoute.Robots {
  return {
    rules: process.env.NODE_ENV === 'production'
      ? [{ userAgent: '*', allow: '/' }]
      : [{ userAgent: '*', disallow: '/' }],
    sitemap: `${BASE_URL}/sitemap.xml`,
  }
}
```

---

## Step 4 — Fonts

### `lib/seo/fonts.ts`
```ts
import { $BODY_FONT } from 'next/font/google'
export const fontSans = $BODY_FONT({ subsets: ['latin'], display: 'swap', variable: '--font-sans' })
```

Apply in `app/layout.tsx`:
```tsx
<html className={fontSans.variable}>
  <body className="font-sans">...</body>
</html>
```

---

## Step 5 — Per-page metadata pattern

For every page, either:
```ts
// Static
export const metadata = buildMetadata({ title: '...', description: '...', path: '/...' })
// Dynamic
export async function generateMetadata({ params }) {
  const data = await fetch(...)
  return buildMetadata({ title: data.title, description: data.desc, path: `/.../${params.slug}` })
}
```

---

## Performance rules (enforce on all pages)

- **Images**: always `next/image` with `width` + `height` or `fill`. Never raw `<img>`.
- **LCP images**: add `priority` prop on the largest above-the-fold image.
- **Fonts**: use `lib/seo/fonts.ts` — never `@import` in CSS.
- **No layout shift**: fix dimensions on images and skeleton-loaded content.

---

## Post-scaffold TODOs

| File | TODO |
|---|---|
| `lib/seo/metadata.ts` | Replace placeholder site name and description |
| `lib/seo/structured-data.ts` | Fill in org name, logo URL, social profiles |
| `app/sitemap.ts` | Add all static routes; uncomment dynamic routes block |
| `lib/seo/fonts.ts` | Replace Inter with brand font if needed |
| `app/layout.tsx` | Add `<JsonLd>` and font variables |

Reference implementation: `templates/project-scaffold/website/` in the infiniteleverage-8-agents-template repo.
