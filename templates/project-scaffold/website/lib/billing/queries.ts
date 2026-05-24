'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

export interface Subscription {
  id: string
  user_id: string
  stripe_customer_id: string | null
  stripe_subscription_id: string | null
  plan: 'free' | 'pro' | 'enterprise'
  status: 'active' | 'canceled' | 'past_due' | 'trialing'
  current_period_end: string | null
  created_at: string
  updated_at: string
}

// ---------------------------------------------------------------------------
// Query: current user's subscription
// ---------------------------------------------------------------------------

export function useSubscription() {
  return useQuery<Subscription | null>({
    queryKey: ['subscription'],
    queryFn: async () => {
      const res = await fetch('/api/billing/subscription')
      if (res.status === 404) return null
      if (!res.ok) throw new Error('Failed to fetch subscription')
      return res.json() as Promise<Subscription>
    },
  })
}

// ---------------------------------------------------------------------------
// Mutation: start a Stripe Checkout session
// ---------------------------------------------------------------------------

interface CheckoutInput {
  priceId: string
  successUrl?: string
  cancelUrl?: string
}

export function useCheckoutSession() {
  return useMutation<void, Error, CheckoutInput>({
    mutationFn: async ({ priceId, successUrl, cancelUrl }) => {
      const res = await fetch('/api/billing/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ priceId, successUrl, cancelUrl }),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({})) as { error?: string }
        throw new Error(body.error ?? 'Failed to create checkout session')
      }
      const { url } = await res.json() as { url: string }
      window.location.href = url
    },
  })
}

// ---------------------------------------------------------------------------
// Mutation: open the Stripe Customer Portal
// ---------------------------------------------------------------------------

interface PortalInput {
  returnUrl?: string
}

export function usePortalSession() {
  const queryClient = useQueryClient()
  return useMutation<void, Error, PortalInput | void>({
    mutationFn: async (input) => {
      const res = await fetch('/api/billing/portal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input ?? {}),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({})) as { error?: string }
        throw new Error(body.error ?? 'Failed to create portal session')
      }
      const { url } = await res.json() as { url: string }
      // Invalidate subscription cache when user returns from portal
      await queryClient.invalidateQueries({ queryKey: ['subscription'] })
      window.location.href = url
    },
  })
}
