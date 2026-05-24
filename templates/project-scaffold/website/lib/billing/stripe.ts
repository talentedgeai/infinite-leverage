import Stripe from 'stripe'

// TODO: Set STRIPE_SECRET_KEY in your environment variables before deploying.
// Get your keys at https://dashboard.stripe.com/apikeys
// TODO: Update apiVersion when Stripe releases a newer stable version.
export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-01-27.acacia',
})
