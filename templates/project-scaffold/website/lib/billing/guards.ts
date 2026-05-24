import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'

type Plan = 'free' | 'pro' | 'enterprise'

const PLAN_RANK: Record<Plan, number> = {
  free: 0,
  pro: 1,
  enterprise: 2,
}

/**
 * Server-side guard for protected route segments.
 * Uses supabase.auth.getUser() — never getSession() (session is not verified server-side).
 * Redirects to /pricing if the user's plan does not meet the minimum required plan.
 *
 * Usage in a Server Component or layout:
 *   await requirePlan('pro')
 */
export async function requirePlan(minPlan: 'pro' | 'enterprise' = 'pro') {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) redirect('/login')

  const { data: subscription } = await supabase
    .from('subscriptions')
    .select('plan, status')
    .eq('user_id', user.id)
    .maybeSingle()

  const plan = (subscription?.plan ?? 'free') as Plan
  const status = subscription?.status ?? 'active'

  // canceled or past_due subscriptions lose access
  const isActive = status === 'active' || status === 'trialing'
  const hasRank = PLAN_RANK[plan] >= PLAN_RANK[minPlan]

  if (!isActive || !hasRank) redirect('/pricing')

  return subscription
}

/**
 * Feature flag check for use in Server Components.
 * Returns true if the user's current plan includes the given feature.
 *
 * TODO: Update this map to match your actual feature flags.
 */
const FEATURE_MAP: Record<string, Plan[]> = {
  // Example: 'advanced_analytics' is available on pro and enterprise
  advanced_analytics: ['pro', 'enterprise'],
  // Example: 'custom_branding' is enterprise-only
  custom_branding: ['enterprise'],
  // Example: 'api_access' is available on pro and enterprise
  api_access: ['pro', 'enterprise'],
}

export async function isFeatureEnabled(userId: string, feature: string): Promise<boolean> {
  const supabase = await createClient()

  const { data: subscription } = await supabase
    .from('subscriptions')
    .select('plan, status')
    .eq('user_id', userId)
    .maybeSingle()

  const plan = (subscription?.plan ?? 'free') as Plan
  const status = subscription?.status ?? 'active'
  const isActive = status === 'active' || status === 'trialing'

  if (!isActive) return false

  const allowedPlans = FEATURE_MAP[feature]
  if (!allowedPlans) return false

  return allowedPlans.includes(plan)
}
