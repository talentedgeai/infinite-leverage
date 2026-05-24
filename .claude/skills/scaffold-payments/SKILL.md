---
name: scaffold-payments
description: >-
  Stamps Stripe Checkout + subscription management (checkout session, webhook handler,
  subscriptions table, feature-gate guard) into the current Next.js + Supabase project.
  Invoke when a user asks to "add payments", "scaffold Stripe", "add subscriptions", or "add billing".
---

# Scaffold: Stripe Payments & Subscriptions

Stamps a production-ready Stripe billing system into the current project in one pass.
Architecture: Supabase subscriptions table → Stripe Checkout → Webhook handler → Feature-gate guards → TanStack Query hooks → React components.

## Before you start

1. Confirm the project uses **Next.js App Router** + **Supabase** (look for `app/` directory and `@supabase/ssr` imports).
2. Ask these customisation questions — state the default for each:

   - **Stripe Price ID for the main paid plan?** (no default — required, e.g. `price_xxx`)
   - **Plans to support?** (default: `free` and `pro`)
   - **Supabase server client import path?** (default: `@/lib/supabase/server`)
   - **Success URL after checkout?** (default: `/dashboard?upgraded=true`)
   - **Cancel URL after checkout abandonment?** (default: `/pricing`)

3. Note the answers as `$PRICE_ID`, `$PLANS`, `$SUPABASE_PATH`, `$SUCCESS_URL`, `$CANCEL_URL`.

---

## Step 1 — Database migration

Create `supabase/migrations/20260524000001_subscriptions_table.sql`:

```sql
create table subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users not null unique,
  stripe_customer_id text unique,
  stripe_subscription_id text unique,
  plan text not null default 'free',   -- 'free' | 'pro' | 'enterprise'
  status text not null default 'active', -- 'active' | 'canceled' | 'past_due' | 'trialing'
  current_period_end timestamptz,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
alter table subscriptions enable row level security;
create policy "user reads own subscription"
  on subscriptions for select using (auth.uid() = user_id);
-- Service role handles all writes via webhook. Users cannot write directly.
```

After creating: `npx supabase db push`

---

## Step 2 — Install dependencies

```bash
npm install stripe @stripe/stripe-js
```

Add required environment variables to `.env.local`:
```
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
```

---

## Step 3 — Stripe client

Create `lib/billing/stripe.ts`:

```ts
import Stripe from 'stripe'
// TODO: Set STRIPE_SECRET_KEY env var
export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-01-27.acacia',
})
```

---

## Step 4 — API routes

### `app/api/billing/checkout/route.ts`

- Auth check via `supabase.auth.getUser()`
- Gets or creates Stripe customer (look up `stripe_customer_id` in subscriptions table; create if missing)
- Creates `stripe.checkout.sessions.create` with `mode: 'subscription'`, `line_items` using `$PRICE_ID`
- `success_url` defaults to `$SUCCESS_URL`, `cancel_url` defaults to `$CANCEL_URL`
- Returns `{ url }` — client does `window.location.href = url`

### `app/api/billing/portal/route.ts`

- Auth check via `supabase.auth.getUser()`
- Looks up `stripe_customer_id` from subscriptions table
- Creates `stripe.billingPortal.sessions.create`
- Returns `{ url }`

### `app/api/billing/webhook/route.ts`

- No auth check — Stripe webhook signature verification instead
- Use `req.text()` (raw body) for signature verification — **not** `req.json()`
- `stripe.webhooks.constructEvent(body, sig, STRIPE_WEBHOOK_SECRET)`
- Handles: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
- Upserts `subscriptions` table using **service role client** (not user client — no session in webhook context)
- Returns 200 immediately

---

## Step 5 — Billing guards

Create `lib/billing/guards.ts`:

- `requirePlan(minPlan)` — server-side guard for protected route segments. Uses `supabase.auth.getUser()` (never `getSession()`). Redirects to `/pricing` if plan check fails.
- `isFeatureEnabled(userId, feature)` — returns boolean for feature flag checks in Server Components.

---

## Step 6 — TanStack Query hooks

Create `lib/billing/queries.ts`:

- `useSubscription()` — fetches current user's subscription via `/api/billing/subscription`
- `useCheckoutSession()` — mutation, calls `POST /api/billing/checkout`, redirects to Stripe
- `usePortalSession()` — mutation, calls `POST /api/billing/portal`, redirects to Stripe

---

## Step 7 — UI components

Create `components/billing/UpgradeButton.tsx`:
- Client component (`'use client'`)
- Calls `useCheckoutSession().mutate({ priceId })`
- Shows loading state during redirect
- Props: `priceId: string`, `label?: string`, `className?: string`

Create `components/billing/PricingCard.tsx`:
- Presentational component
- Props: `plan: string`, `price: number`, `currency: string`, `interval: 'month' | 'year'`, `features: string[]`, `priceId: string`, `highlighted?: boolean`
- Renders price, feature list, `<UpgradeButton>`

---

## Step 8 — Post-scaffold TODOs (leave as comments in the code)

| File | TODO |
|---|---|
| `lib/billing/stripe.ts` | Set `STRIPE_SECRET_KEY` env var; update `apiVersion` if Stripe releases a newer stable |
| `app/api/billing/webhook/route.ts` | Add handling for `invoice.payment_failed` if you send dunning emails |
| `lib/billing/guards.ts` | Update `isFeatureEnabled` map to match your feature flags |
| `components/billing/PricingCard.tsx` | Replace Tailwind classes with project design system |

---

## Step 9 — Verify

```bash
npx tsc --noEmit   # must pass with 0 errors before handing off
```

Reference implementation: `templates/project-scaffold/website/` in the infiniteleverage-8-agents-template repo.
Setup notes: `templates/project-scaffold/website/docs/billing/setup-notes.md`.
