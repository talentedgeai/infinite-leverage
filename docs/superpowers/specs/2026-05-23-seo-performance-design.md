# SEO + Performance — Next.js App Router

> Reference spec for scaffolding SEO, metadata, structured data, and Core Web Vitals into any Next.js project.
> Status: Approved

## Architecture

Four layers:
1. **Metadata helpers** — base config + `generateMetadata` patterns
2. **Structured data** — JSON-LD components for common schema types
3. **Sitemap + robots** — Next.js App Router native files
4. **Performance** — image, font, and loading best practices

## Metadata strategy

### Base metadata (`lib/seo/metadata.ts`)
Single source of truth for site-wide defaults. Every page merges with this base via Next.js metadata merging.

### Page-level metadata
Static pages: export `metadata` object.
Dynamic pages: export `generateMetadata` async function — fetches data and builds metadata.

### Open Graph
Every page gets `og:title`, `og:description`, `og:image`, `og:url`.
Default OG image lives at `app/opengraph-image.png` (Next.js serves it automatically).

## Structured data

Use `application/ld+json` script tags injected via `<JsonLd>` component.
Common schemas: `WebSite`, `Organization`, `Article`, `BreadcrumbList`, `Product`.

## Sitemap

`app/sitemap.ts` exports a function returning `MetadataRoute.Sitemap`.
Static routes hardcoded; dynamic routes (blog posts, products) fetched from Supabase.

## Robots

`app/robots.ts` — allow all crawlers in production, block in preview/staging.

## Performance rules

- **Images**: always `next/image` with explicit `width` + `height` or `fill`. Never `<img>`.
- **Fonts**: `next/font/google` with `display: 'swap'` and `preload: true`. Never @import.
- **LCP**: above-the-fold images get `priority` prop on `next/image`.
- **CLS**: reserve space for images and dynamic content with fixed dimensions.
- **No layout shift on font load**: use CSS variables from `next/font`.

## File map

| File | Responsibility |
|---|---|
| `lib/seo/metadata.ts` | Base metadata config + helper functions |
| `lib/seo/structured-data.ts` | JSON-LD schema builder functions |
| `components/seo/JsonLd.tsx` | Renders JSON-LD script tag |
| `app/sitemap.ts` | Next.js sitemap route |
| `app/robots.ts` | Next.js robots.txt route |
| `lib/seo/fonts.ts` | next/font configuration |
