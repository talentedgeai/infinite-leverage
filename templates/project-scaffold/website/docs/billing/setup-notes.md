# Billing Setup Notes

Step-by-step checklist for wiring up Stripe billing in this project.

---

## 1. Required environment variables

Add all three to `.env.local` (development) and your Vercel project settings (production):

```
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
NEXT_PUBLIC_APP_URL=https://your-domain.com
```

Get your keys at https://dashboard.stripe.com/apikeys.  
Get `STRIPE_WEBHOOK_SECRET` from https://dashboard.stripe.com/webhooks after completing step 4.

---

## 2. Run the database migration

```bash
npx supabase db push
```

This creates the `subscriptions` table with RLS enabled.
Users can read their own row. The webhook handler writes via the service role client.

---

## 3. Install the Stripe npm package

```bash
npm install stripe @stripe/stripe-js
```

---

## 4. Register the webhook endpoint in Stripe

1. Go to https://dashboard.stripe.com/webhooks
2. Click **Add endpoint**
3. Endpoint URL: `https://your-domain.com/api/billing/webhook`
4. Select these events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_failed` *(optional — add if sending dunning emails)*
5. Copy the **Signing secret** → paste as `STRIPE_WEBHOOK_SECRET`

For local development, use the Stripe CLI:
```bash
stripe listen --forward-to localhost:3000/api/billing/webhook
```
The CLI prints a local webhook secret — use that as `STRIPE_WEBHOOK_SECRET` in `.env.local`.

---

## 5. Configure the Stripe Customer Portal

1. Go to https://dashboard.stripe.com/settings/billing/portal
2. Enable the portal
3. Configure allowed actions (cancel, change plan, update payment method)

---

## 6. Create your products and prices in Stripe

1. Go to https://dashboard.stripe.com/products
2. Create a product for each plan (e.g. "Pro", "Enterprise")
3. Add a recurring price to each product
4. Copy the **Price ID** (format: `price_xxx`) — pass this as `priceId` to `<UpgradeButton>` and `<PricingCard>`

---

## 7. Map price IDs to plan names

Open `app/api/billing/webhook/route.ts` and update `planFromSubscription()`:

```ts
function planFromSubscription(subscription: Stripe.Subscription): string {
  const priceId = subscription.items.data[0]?.price.id ?? ''
  if (priceId === 'price_your_enterprise_price_id') return 'enterprise'
  if (priceId === 'price_your_pro_price_id') return 'pro'
  return 'free'
}
```

---

## 8. Update feature flags

Open `lib/billing/guards.ts` and update `FEATURE_MAP` to match your features:

```ts
const FEATURE_MAP: Record<string, Plan[]> = {
  advanced_analytics: ['pro', 'enterprise'],
  custom_branding: ['enterprise'],
  api_access: ['pro', 'enterprise'],
}
```

---

## Files created by this scaffold

| File | Purpose |
|---|---|
| `supabase/migrations/20260524000001_subscriptions_table.sql` | DB schema + RLS |
| `lib/billing/stripe.ts` | Stripe client singleton |
| `lib/billing/guards.ts` | `requirePlan` + `isFeatureEnabled` server guards |
| `lib/billing/queries.ts` | TanStack Query hooks for subscription, checkout, portal |
| `app/api/billing/checkout/route.ts` | Creates Stripe Checkout session |
| `app/api/billing/portal/route.ts` | Creates Stripe Customer Portal session |
| `app/api/billing/webhook/route.ts` | Handles Stripe webhook events |
| `components/billing/UpgradeButton.tsx` | Client component — triggers checkout |
| `components/billing/PricingCard.tsx` | Presentational pricing card |

---

## Post-scaffold TODOs

- [ ] Set all environment variables (local + Vercel)
- [ ] Run `npx supabase db push`
- [ ] Register webhook endpoint in Stripe dashboard
- [ ] Configure Stripe Customer Portal
- [ ] Create products + prices in Stripe, update `planFromSubscription()`
- [ ] Update `FEATURE_MAP` in `guards.ts`
- [ ] Replace Tailwind classes in `PricingCard.tsx` with project design system
- [ ] Add `invoice.payment_failed` handler if you send dunning emails
- [ ] Add a `GET /api/billing/subscription` route to serve `useSubscription()` hook
