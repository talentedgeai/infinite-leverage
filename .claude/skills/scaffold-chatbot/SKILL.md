---
name: scaffold-chatbot
description: >-
  Stamps the multi-session AI chatbot pattern (ChatGPT/Claude/Gemini style) into
  the current Next.js + Supabase project. Covers schema, streaming API route,
  session management, and full UI. Invoke when a user asks to "add chatbot",
  "add multi-session chat", "scaffold AI chat", or similar.
---

# Scaffold: Multi-Session AI Chatbot

Stamps a production-ready multi-session AI chatbot into the current project in one pass.
Architecture: Supabase persistence → Next.js API routes → TanStack Query → Zustand → React UI (AI SDK v6).

## Before you start

1. Confirm the project uses **Next.js App Router** + **Supabase** (look for `app/` directory and `supabase/` or `@supabase/ssr` imports).
2. Ask these customisation questions — state the default for each:

   - **Default AI model?** (default: `anthropic/claude-sonnet-4.6` — any `provider/model` string works via AI Gateway)
   - **Chat route path?** (default: `/chat`)
   - **Supabase server client import path?** (default: `@/lib/supabase/server`)
   - **Add auth guard on the chat page?** (default: yes — wraps page in a session check; requires auth to be set up)

3. Note the answers as `$MODEL`, `$CHAT_PATH`, `$SUPABASE_PATH`, `$AUTH_GUARD`.

---

## Step 1 — Database migration

Create `supabase/migrations/<timestamp>_chat_tables.sql`:

```sql
-- chat_sessions: one row per conversation
create table chat_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users not null,
  title text not null default 'New Chat',
  model text not null default '$MODEL',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
alter table chat_sessions enable row level security;
create policy "user owns sessions"
  on chat_sessions for all using (auth.uid() = user_id);

-- chat_messages: parts stored as jsonb — maps 1:1 to UIMessage.parts from AI SDK v6
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
```

After creating: `npx supabase db push`

---

## Step 2 — Install dependencies

```bash
npm install ai @ai-sdk/react @ai-sdk/elements zustand
```

Pull AI Gateway credentials (preferred — OIDC, no manual rotation):
```bash
vercel env pull .env.local
```

Fallback (no Vercel project linked): add a manual API key from `vercel.com/[team]/~/ai-gateway/api-keys` to `.env.local`. The `ai` package picks it up automatically at runtime.

---

## Step 3 — Constants

Create `lib/chat/constants.ts`:
```ts
export const DEFAULT_CHAT_MODEL = '$MODEL'
export const TITLE_MODEL = 'anthropic/claude-haiku-4.5'
```

---

## Step 4 — API routes

### `app/api/sessions/route.ts` — list + create

```ts
import { createClient } from '$SUPABASE_PATH'
import { NextResponse } from 'next/server'
import { DEFAULT_CHAT_MODEL } from '@/lib/chat/constants'

export async function GET() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return new NextResponse('Unauthorized', { status: 401 })
  const { data, error } = await supabase
    .from('chat_sessions')
    .select('id, title, model, created_at, updated_at')
    .eq('user_id', user.id)
    .order('updated_at', { ascending: false })
  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return NextResponse.json(data)
}

export async function POST(req: Request) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return new NextResponse('Unauthorized', { status: 401 })
  const body = await req.json().catch(() => ({}))
  const model = body.model ?? DEFAULT_CHAT_MODEL
  const { data, error } = await supabase
    .from('chat_sessions')
    .insert({ user_id: user.id, model })
    .select('id, title, model, created_at, updated_at')
    .single()
  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return NextResponse.json(data, { status: 201 })
}
```

### `app/api/sessions/[id]/route.ts` — rename + delete

```ts
import { createClient } from '$SUPABASE_PATH'
import { NextResponse } from 'next/server'

export async function PATCH(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return new NextResponse('Unauthorized', { status: 401 })
  const { title } = await req.json()
  if (!title?.trim()) return NextResponse.json({ error: 'title is required' }, { status: 400 })
  const { error } = await supabase.from('chat_sessions')
    .update({ title: title.trim() }).eq('id', id).eq('user_id', user.id)
  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return new NextResponse(null, { status: 204 })
}

export async function DELETE(_req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return new NextResponse('Unauthorized', { status: 401 })
  const { error } = await supabase.from('chat_sessions')
    .delete().eq('id', id).eq('user_id', user.id)
  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return new NextResponse(null, { status: 204 })
}
```

### `app/api/sessions/[id]/messages/route.ts` — history

```ts
import { createClient } from '$SUPABASE_PATH'
import { NextResponse } from 'next/server'
import type { UIMessage } from 'ai'

export async function GET(_req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return new NextResponse('Unauthorized', { status: 401 })
  // Ownership check first — RLS is safety net, not primary guard
  const { data: session } = await supabase.from('chat_sessions')
    .select('id').eq('id', id).eq('user_id', user.id).single()
  if (!session) return new NextResponse('Not Found', { status: 404 })
  const { data, error } = await supabase.from('chat_messages')
    .select('id, role, parts, created_at')
    .eq('session_id', id).eq('user_id', user.id)
    .order('created_at', { ascending: true }).limit(100)
  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  const messages: UIMessage[] = (data ?? []).map(row => ({
    id: row.id, role: row.role as UIMessage['role'], parts: row.parts,
  }))
  return NextResponse.json(messages)
}
```

### `app/api/chat/route.ts` — streaming + auto-title

Key patterns (client sends only `{ message, sessionId }` — server loads full history):

```ts
import { convertToModelMessages, generateText, streamText, type UIMessage } from 'ai'
import { createClient } from '$SUPABASE_PATH'
import { TITLE_MODEL } from '@/lib/chat/constants'
export const maxDuration = 60

export async function POST(req: Request) {
  // 1. Auth check
  // 2. Verify session ownership (.eq('user_id', user.id))
  // 3. Count messages → isFirstMessage = count === 0
  // 4. Save user message to chat_messages
  // 5. Load full history from DB (server owns history, not client)
  // 6. streamText({ model: session.model, messages: convertToModelMessages(history) })
  // 7. toUIMessageStreamResponse({ onFinish: save assistant + bump updated_at + auto-title })
  // Auto-title: fire-and-forget generateText({ model: TITLE_MODEL }) on isFirstMessage
}
```

See full implementation in `templates/project-scaffold/website/app/api/chat/route.ts`.

---

## Step 5 — Zustand store + TanStack Query hooks

`lib/chat/store.ts` — minimal, activeSessionId only:
```ts
import { create } from 'zustand'
interface ChatStore { activeSessionId: string | null; setActiveSession: (id: string | null) => void }
export const useChatStore = create<ChatStore>((set) => ({
  activeSessionId: null,
  setActiveSession: (id) => set({ activeSessionId: id }),
}))
```

`lib/chat/queries.ts` — exports: `useSessions`, `useSessionMessages`, `useCreateSession`, `useDeleteSession`, `useRenameSession`.
See full implementation in `templates/project-scaffold/website/lib/chat/queries.ts`.

---

## Step 6 — UI components

Create all components under `components/chat/`. Key patterns:

**`ChatWindow.tsx`** — `key={sessionId}` forces remount on session switch (prevents useChat state bleed):
```tsx
export function ChatWindow() {
  const sessionId = useChatStore(s => s.activeSessionId)
  if (!sessionId) return <EmptyState />
  return <ChatWindowInner key={sessionId} sessionId={sessionId} />
}
```

**`ChatWindowInner.tsx`** — useChat must be called unconditionally (React rules):
```tsx
const { data: initialMessages, isLoading } = useSessionMessages(sessionId)
const { messages, sendMessage, status } = useChat({
  id: sessionId,
  messages: initialMessages,   // undefined until loaded — do NOT fallback to []
  transport: new DefaultChatTransport({ api: '/api/chat', body: { sessionId } }),
})
if (isLoading) return <LoadingSkeleton />
```

**`MessageBubble.tsx`** — use `isToolUIPart` from `'ai'` as a catch-all for typed tool parts, use AI Elements for text/reasoning:
```tsx
import { isToolUIPart, type UIMessage } from 'ai'
import { Response, Reasoning } from '@ai-sdk/elements'
// Render: text → <Response>, reasoning → <Reasoning>, tool → <ToolCallBlock>
```

**`ToolCallBlock.tsx`** — typed parts:
```tsx
type AnyPart = UIMessage['parts'][number]
interface Props { part: AnyPart & { type: `tool-${string}` } }
```

**`MessageList.tsx`** — status type inline (do not import from @ai-sdk/react):
```tsx
interface Props { messages: UIMessage[]; status: 'idle' | 'streaming' | 'submitted' | 'error' }
```

**`SessionItem.tsx`** — use `<button type="button" aria-pressed={isActive}>` not a `<div>`.

See full implementations in `templates/project-scaffold/website/components/chat/`.

---

## Step 7 — Layout + page route

```tsx
// app/$CHAT_PATH/page.tsx
// TODO: wrap in auth guard if $AUTH_GUARD = yes
import { ChatLayout } from '@/components/chat/ChatLayout'
export default function ChatPage() { return <ChatLayout /> }
```

---

## Step 8 — Post-scaffold TODOs (leave as comments in the code)

Mark these in the generated files:

| File | TODO |
|---|---|
| `lib/chat/constants.ts` | Swap `DEFAULT_CHAT_MODEL` for your preferred model |
| `app/$CHAT_PATH/page.tsx` | Add auth guard (redirect unauthenticated users) |
| `components/chat/MessageBubble.tsx` | Replace Tailwind classes with project design system |
| `components/chat/ChatInput.tsx` | Replace Tailwind classes with project design system |
| `components/chat/SessionSidebar.tsx` | Replace Tailwind classes with project design system |
| `app/api/chat/route.ts` | Add system prompt, tools, or stopWhen logic per feature needs |

---

## Step 9 — Verify

```bash
npx tsc --noEmit   # must pass with 0 errors before handing off
```

Reference implementation: `templates/project-scaffold/website/` in the infiniteleverage-8-agents-template repo.
QA checklist: `templates/project-scaffold/website/docs/chat-qa-checklist.md`.
