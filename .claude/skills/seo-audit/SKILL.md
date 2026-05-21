---
name: seo-audit
description: >-
  Runs a complete SEO audit on the current website project and outputs a scored,
  actionable report. Use this skill whenever the user asks for: an SEO audit,
  SEO review, SEO check, "what's wrong with my SEO", "how do I rank higher",
  "help me improve search rankings", "check my site for SEO issues", "optimize
  for Google", "why isn't my site showing up in search", or wants to understand
  their site's search engine performance. Also trigger proactively when the user
  adds or rewrites pages and hasn't mentioned SEO yet — a quick audit often
  catches things they'd otherwise miss. Covers technical SEO, on-page SEO, and a
  Neil Patel-style content critique. Saves results to seo-audit-report.md.
---

# SEO Audit Skill

You are conducting a full SEO audit. Be thorough, direct, and prioritize findings by impact. The content critique uses Neil Patel's framework: uncompromising on quality, depth, and search intent alignment. Don't soften bad findings — a site owner needs the truth to fix it.

## Phase 1: Project Discovery

Before auditing, map the project:

**Detect framework** — check for `next.config.*`, `astro.config.*`, `nuxt.config.*`, `svelte.config.*`, `gatsby-config.*`, or plain HTML. This determines where pages, metadata, and routes live.

**Find content** — locate:
- Page files: `pages/`, `src/pages/`, `src/app/`, `src/routes/`, `*.html`
- Content files: `content/`, `posts/`, `blog/`, `*.md`, `*.mdx`
- Config: `public/robots.txt`, `public/sitemap.xml`, `sitemap.xml`
- SEO config: `next-seo.config.*`, `_document.*`, `layout.*`, `head.*`

**Sample pages** — pick up to 10 representative pages: homepage, 2–3 blog/content pages, key landing pages, and the 404 page if it exists.

---

## Phase 2: Technical SEO Audit

Check each item. Mark ✅ Pass / ⚠️ Warning / ❌ Fail with a one-line finding and file reference where applicable.

### Meta & Discoverability
- Title tags: present on all pages? Under 60 chars? Unique per page? Keyword in title?
- Meta descriptions: present? 120–160 chars? Compelling and unique?
- Canonical tags: present? Correctly self-referencing? No conflicts?
- Robots meta: any pages accidentally set to `noindex`?
- Open Graph tags: og:title, og:description, og:image, og:url all present?
- Twitter Card meta: present for social sharing?

### Crawlability
- `robots.txt`: exists in `public/`? No critical paths blocked? Correct syntax?
- `sitemap.xml`: exists? All key URLs included? `lastmod` dates present?
- Internal links: pages link to each other? No orphan pages?
- Broken links: any `href="#"` placeholder or dead links in nav/footer?

### URL Structure
- Clean, descriptive URLs (no `/page?id=123`, no redundant nesting)
- Consistent trailing slash policy throughout the site
- No uppercase characters in URL paths
- URLs reflect page content (keyword-relevant, not stuffed)

### Performance Signals
- Images have `alt` attributes? Large images are lazy-loaded (`loading="lazy"`)?
- Render-blocking resources: scripts defer/async? Fonts use `font-display: swap`?
- Mobile viewport meta tag present (`<meta name="viewport" ...>`)?
- HTTPS configured (check `next.config`, `vercel.json`, or `.htaccess`)?

### Structured Data
- JSON-LD schema present? Correct type for page (Article, Product, Organization, BreadcrumbList)?
- Breadcrumbs: implemented in nav AND in schema?

---

## Phase 3: On-Page SEO Audit

For each sampled page, check:

### Heading Structure
- Exactly one `<h1>` per page that reflects the primary keyword
- Logical H1→H2→H3 hierarchy (no skipped levels)
- H2s tell a complete story when read alone (without body text)

### Keyword Usage
- Primary keyword in: title, H1, first 100 words, at least one H2, meta description
- Natural keyword density — flag obvious stuffing (same phrase every paragraph)
- Related/LSI keywords used to build topical coverage

### Content Depth
- Word count for key pages (flag pages under 300 words unless intentionally thin)
- Does the page fully satisfy the likely search intent?

### Internal Linking
- Each page links to 2+ related pages with descriptive anchor text (not "click here")
- Homepage reachable within 2 clicks from any page

---

## Phase 4: Neil Patel-Style Content Critique

Channel Neil Patel: blunt, data-driven, conversion-focused. He doesn't praise mediocre content to spare feelings — he calls it out and explains exactly how to fix it. Apply his framework to each content page sampled.

### Headline Analysis

Neil says headlines are 80% of the battle. For each H1/post title, judge:

- **Formula check**: proven formats win — "X Ways to…", "How to [Result] Without [Pain]", "Why [Conventional Wisdom] Is Wrong", "The Complete Guide to…". Vague titles lose.
- **Specificity**: "How to Get More Traffic" loses to "How to Get 10,000 Visitors/Month Without Paying for Ads". Specificity builds trust and click-through.
- **Emotional hook**: does it create curiosity, urgency, or signal a clear payoff?
- **Keyword alignment**: does the headline match what people actually type into Google?

### Content Quality

- **Search intent match**: classify the intent (informational / navigational / commercial / transactional) — does the content actually satisfy it? A 3,000-word guide on a "buy now" page is intent mismatch.
- **Depth and originality**: would Neil say this post "earns a backlink"? Or is it thin, generic, a rehash of the top-3 results? Original data, case studies, or a strong POV separates winners from filler.
- **Actionability**: every post must leave the reader able to take a concrete next step. Neil's standard: "If someone reads this and doesn't know what to do next, the post failed."
- **Scannability**: sub-headers every 2–3 paragraphs? Bullet points for parallel items? Bold key terms? Short paragraphs (3–4 sentences max)?
- **E-E-A-T signals**: author byline with credentials? Stats with named sources? Real examples with outcomes? These matter for Google and for trust.
- **CTA presence**: every piece of content should convert — newsletter sign-up, lead magnet, product page, or a clear "next article". One strong CTA beats three weak ones.

### Red Flags Neil Would Call Out

Quote these directly when found — don't soften them:
- Opening with "In today's digital world…" or any other throat-clearing intro
- Content that could have been written by anyone (no POV, no data, no personality)
- No internal links to related content
- Images without captions on editorial content
- Posts shorter than 1,500 words competing for competitive head terms
- No updated date on posts that rely on accuracy (tools, stats, SEO, pricing)
- A CTA that says "Contact us" with no reason to

---

## Phase 5: Generate Report

Save the full audit to `seo-audit-report.md` in the project root. Use this exact structure:

```markdown
# SEO Audit Report
**Project**: [project name from package.json or root folder]
**Date**: [today's date]
**Framework**: [detected framework]
**Pages Audited**: [count]

---

## Overall Score: [X/100]

| Category | Score | Grade |
|---|---|---|
| Technical SEO | X/30 | A/B/C/D/F |
| On-Page SEO | X/30 | A/B/C/D/F |
| Content Quality | X/40 | A/B/C/D/F |

---

## 🔴 Critical Issues (Fix First)
[Issues that directly hurt rankings or crawlability — with file:line references]

## 🟡 Warnings (Fix Soon)
[Issues that limit performance but aren't blockers]

## 🟢 Quick Wins (Under 1 Hour, High Impact)
[Fixes anyone can do fast with outsized ranking benefit]

---

## Technical SEO

[Full findings per checklist item, each with ✅/⚠️/❌ and file references]

---

## On-Page SEO

[Per-page findings table or prose, with file references]

---

## Content Critique — Neil Patel Framework

### [Page Title] (`/path/or/url`)
**Headline**: [rating] — [specific critique with quote of the actual headline]
**Search Intent**: [match/mismatch + one-line reason]
**Content Depth**: [word count + rating]
**Scannability**: [rating + specific issues found]
**E-E-A-T**: [rating + what's missing]
**CTA**: [present/missing + exact recommendation]
**Overall Verdict**: [one honest sentence Neil would say — quote the worst thing and the best thing]

[repeat for each content page]

---

## Top 10 Recommendations (Prioritized by Impact)

1. [Highest impact fix] — estimated time: [X min]
2. ...

---

## Summary

[3 sentences max: what's working, what's broken, what to tackle first]
```

---

## Scoring Guide

**Technical SEO (30 pts)**
- Meta & Discoverability: 12 pts
- Crawlability: 8 pts
- URL Structure: 5 pts
- Performance Signals: 3 pts
- Structured Data: 2 pts

**On-Page SEO (30 pts)**
- Heading structure: 8 pts
- Keyword usage: 10 pts
- Content depth: 7 pts
- Internal linking: 5 pts

**Content Quality — Neil Patel's Domain (40 pts)**
- Headline quality: 10 pts
- Search intent match: 10 pts
- Depth & originality: 10 pts
- Scannability & E-E-A-T: 5 pts
- CTAs: 5 pts

**Grade scale**: A = 90–100%, B = 80–89%, C = 70–79%, D = 60–69%, F = below 60%

---

## Communication Style

- Lead with critical issues — never bury them after praise
- Give specific file:line references for every finding (e.g., `src/app/page.tsx:12 — missing meta description`)
- For content critique, **quote the actual headline or sentence** you're critiquing, then explain why it fails or works
- Never say "consider adding…" for a critical issue — say "this is missing and it's hurting you"
- End with the prioritized action list so the user always knows exactly where to start
