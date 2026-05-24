-- supabase/migrations/20260522000000_chat_tables.sql

-- chat_sessions
create table chat_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users not null,
  title text not null default 'New Chat',
  model text not null default 'anthropic/claude-sonnet-4.6',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
alter table chat_sessions enable row level security;
create policy "user owns sessions"
  on chat_sessions for all using (auth.uid() = user_id);

-- chat_messages
create table chat_messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references chat_sessions on delete cascade not null,
  user_id uuid references auth.users not null,
  role text check (role in ('user','assistant','tool')) not null,
  parts jsonb not null,
  created_at timestamptz default now()
);
alter table chat_messages enable row level security;
create policy "user owns messages"
  on chat_messages for all using (auth.uid() = user_id);

create index on chat_messages(session_id, created_at);
