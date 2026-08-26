// lib/supabase/service.ts
import { createClient as createSupabaseClient } from '@supabase/supabase-js'

/**
 * Service-role client. Bypasses RLS — use ONLY in server-side code that must
 * write rows the signed-in user is not allowed to write themselves.
 *
 * The `subscriptions` table is the motivating case: its RLS policy is
 * SELECT-only on purpose, because a user who could write their own row could
 * set `plan: 'enterprise'` and skip paying. Billing state is therefore written
 * exclusively through this client, from code paths the user cannot forge.
 *
 * Never import this into a Client Component, and never hand its results
 * straight back to a caller without filtering by the caller's own user id.
 */
export function createServiceClient() {
  const key = process.env.SUPABASE_SECRET_KEY
  if (!key) {
    throw new Error(
      'SUPABASE_SECRET_KEY is not set — service-role writes (billing) will fail. ' +
        'Add it to .env.local and to your deployment environment.'
    )
  }
  return createSupabaseClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, key, {
    auth: { persistSession: false, autoRefreshToken: false },
  })
}
