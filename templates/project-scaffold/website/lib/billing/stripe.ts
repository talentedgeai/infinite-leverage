import Stripe from 'stripe'

// TODO: Set STRIPE_SECRET_KEY in your environment variables before deploying.
// Get your keys at https://dashboard.stripe.com/apikeys
// TODO: Update apiVersion when Stripe releases a newer stable version.
// Fallback placeholder keeps `next build` from crashing before the key is
// configured — real API calls will fail until STRIPE_SECRET_KEY is set.
export const stripe = new Stripe(
  process.env.STRIPE_SECRET_KEY ?? 'sk_test_placeholder',
  {
    apiVersion: '2026-07-29.dahlia',
  }
)
