import { NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'
import { createServiceClient } from '@/lib/supabase/service'
import { stripe } from '@/lib/billing/stripe'

export async function POST(req: Request) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return new NextResponse('Unauthorized', { status: 401 })

  const body = await req.json().catch(() => ({})) as {
    priceId?: string
    successUrl?: string
    cancelUrl?: string
  }

  const priceId = body.priceId
  if (!priceId) {
    return NextResponse.json({ error: 'priceId is required' }, { status: 400 })
  }

  const successUrl = body.successUrl ?? `${process.env.NEXT_PUBLIC_APP_URL}/dashboard?upgraded=true`
  const cancelUrl = body.cancelUrl ?? `${process.env.NEXT_PUBLIC_APP_URL}/pricing`

  // Look up or create Stripe customer
  const { data: subscription } = await supabase
    .from('subscriptions')
    .select('stripe_customer_id')
    .eq('user_id', user.id)
    .maybeSingle()

  let customerId = subscription?.stripe_customer_id

  if (!customerId) {
    const customer = await stripe.customers.create({
      email: user.email,
      metadata: { supabase_user_id: user.id },
    })
    customerId = customer.id

    // Persist the Stripe customer id. `subscriptions` is SELECT-only under RLS
    // (a user who could write it could self-grant a paid plan), so this write
    // must go through the service-role client — the user-scoped `supabase`
    // client above is denied here, silently, and the id would be lost.
    const { error: upsertError } = await createServiceClient()
      .from('subscriptions')
      .upsert(
        {
          user_id: user.id,
          stripe_customer_id: customerId,
          plan: 'free',
          status: 'active',
        },
        { onConflict: 'user_id' }
      )

    // Failing closed matters: if the id is not stored, the next checkout finds
    // no customer and mints a SECOND Stripe customer for the same user.
    if (upsertError) {
      console.error('[billing] failed to persist stripe_customer_id', upsertError)
      return NextResponse.json(
        { error: 'Could not start checkout. Please try again.' },
        { status: 500 }
      )
    }
  }

  const session = await stripe.checkout.sessions.create({
    customer: customerId,
    mode: 'subscription',
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: successUrl,
    cancel_url: cancelUrl,
    subscription_data: {
      metadata: { supabase_user_id: user.id },
    },
  })

  return NextResponse.json({ url: session.url })
}
