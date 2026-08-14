import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'
import { stripe } from '@/lib/billing/stripe'
import type Stripe from 'stripe'

// Use secret-key client — no user session in webhook context.
// Never use the user-facing createClient() here.
function createServiceClient() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SECRET_KEY!,
  )
}

function planFromSubscription(subscription: Stripe.Subscription): string {
  // TODO: Map your Stripe price IDs to plan names.
  // Example: if (priceId === 'price_xxx') return 'pro'
  const priceId = subscription.items.data[0]?.price.id ?? ''
  if (priceId.includes('enterprise')) return 'enterprise'
  if (priceId.includes('pro')) return 'pro'
  return 'free'
}

export async function POST(req: Request) {
  // Raw body required for Stripe signature verification — do NOT use req.json()
  const body = await req.text()
  const sig = req.headers.get('stripe-signature')

  if (!sig) {
    return NextResponse.json({ error: 'Missing stripe-signature header' }, { status: 400 })
  }

  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(
      body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET!,
    )
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Webhook signature verification failed'
    return NextResponse.json({ error: message }, { status: 400 })
  }

  // Return 200 immediately — process async so Stripe doesn't time out
  void handleEvent(event)

  return NextResponse.json({ received: true })
}

async function handleEvent(event: Stripe.Event) {
  const supabase = createServiceClient()

  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object as Stripe.Checkout.Session
      if (session.mode !== 'subscription') break

      const userId = session.metadata?.supabase_user_id
      const customerId = session.customer as string
      const subscriptionId = session.subscription as string
      if (!userId) break

      const subscription = await stripe.subscriptions.retrieve(subscriptionId)

      await supabase.from('subscriptions').upsert({
        user_id: userId,
        stripe_customer_id: customerId,
        stripe_subscription_id: subscriptionId,
        plan: planFromSubscription(subscription),
        status: subscription.status,
        current_period_end: new Date(subscription.current_period_end * 1000).toISOString(),
        updated_at: new Date().toISOString(),
      }, { onConflict: 'user_id' })
      break
    }

    case 'customer.subscription.updated': {
      const subscription = event.data.object as Stripe.Subscription
      const userId = subscription.metadata?.supabase_user_id
      if (!userId) break

      await supabase.from('subscriptions').upsert({
        user_id: userId,
        stripe_subscription_id: subscription.id,
        plan: planFromSubscription(subscription),
        status: subscription.status,
        current_period_end: new Date(subscription.current_period_end * 1000).toISOString(),
        updated_at: new Date().toISOString(),
      }, { onConflict: 'user_id' })
      break
    }

    case 'customer.subscription.deleted': {
      const subscription = event.data.object as Stripe.Subscription
      const userId = subscription.metadata?.supabase_user_id
      if (!userId) break

      await supabase.from('subscriptions').upsert({
        user_id: userId,
        stripe_subscription_id: subscription.id,
        plan: 'free',
        status: 'canceled',
        current_period_end: new Date(subscription.current_period_end * 1000).toISOString(),
        updated_at: new Date().toISOString(),
      }, { onConflict: 'user_id' })
      break
    }

    // TODO: Add 'invoice.payment_failed' handler here if you send dunning emails.
    default:
      break
  }
}
