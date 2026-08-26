-- Migration: subscriptions table
-- Tracks Stripe subscription state per user.
-- All writes are performed by the webhook handler using the service role client.
-- Users can read their own row via RLS; they cannot write directly.

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
  on subscriptions for select
  to authenticated
  using ((select auth.uid()) = user_id);

-- SELECT only, deliberately. A user who could write this row could set
-- plan='enterprise' and skip paying, since lib/billing/guards.ts gates features
-- on plan/status. Every write goes through the service-role client in
-- lib/supabase/service.ts (the Stripe webhook, and the checkout route when it
-- first creates the Stripe customer). Do not add an INSERT/UPDATE policy here.
--
-- user_id is `unique`, which already provides the index the SELECT policy needs.
