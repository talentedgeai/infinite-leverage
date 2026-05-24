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
  on subscriptions for select using (auth.uid() = user_id);

-- Service role writes (webhook). User cannot write directly.
-- The webhook upserts using a service role client that bypasses RLS.
