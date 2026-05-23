# AI Chatbot — Multi-Session Reference Guideline

**Date:** 2026-05-22
**Status:** Approved — implementation plan at `docs/superpowers/plans/2026-05-22-ai-chatbot-multi-session.md`
**Scope:** Web-based AI chatbot UI (ChatGPT/Claude/Gemini-style) with multi-session history management. **Auth, SEO, performance, and markdown rendering are intentionally out of scope** — they get their own specs in subsequent cycles.

---

## 1. Purpose

A reusable reference doc that any developer on the team can follow to add a multi-session AI chatbot to a Next.js + Supabase project — without making the same architectural mistakes each time. The doc is the source of truth; code in client repos copies from it.

**Success criteria:**
- A developer who has never built a chatbot before can wire up a working multi-session chat in under one day by following this doc.
- The patterns survive AI SDK and Supabase API churn — when libraries update, only code snippets change; layer boundaries and decisions stay.

---

## 2. Stack (assumed)

- **Framework:** Next.js 16 (App Router), Fluid Compute runtime
- **Database / Auth:** Supabase (Postgres + Auth + RLS)
- **AI:** Vercel AI SDK v6 (`ai`, `@ai-sdk/react`) — multi-provider via provider registry
- **Server state:** TanStack Query v5
- **Forms:** TanStack Form (for chat input validation when needed)
- **Client state:** Zustand (one tiny store for active session)
- **AI message rendering:** AI Elements (`@ai-sdk/elements`) by default — streaming-aware, handles text/reasoning/tool parts safely. A rich-text renderer can be swapped in for the text-part component when a project requires unified rendering across non-chat surfaces; covered by a separate spec.

---

## 3. Architecture

Five strict layers. Each layer talks only to its immediate neighbour.

```
┌─────────────────────────────────────────┐
│  UI Layer (React Components)            │
│  SessionSidebar · ChatWindow · Input    │
├─────────────────────────────────────────┤
│  Chat Hook Layer                        │
│  useChat (@ai-sdk/react) +              │
│  Zustand store for activeSessionId      │
├─────────────────────────────────────────┤
│  Data Layer                             │
│  TanStack Query — session CRUD          │
├─────────────────────────────────────────┤
│  API Layer (Next.js Route Handlers)     │
│  POST /api/chat — streaming             │
│  GET/POST/PATCH/DELETE /api/sessions    │
├─────────────────────────────────────────┤
│  Persistence Layer                      │
│  Supabase — chat_sessions +             │
│  chat_messages, RLS on user_id          │
└─────────────────────────────────────────┘
```

**Key invariants:**
- `useChat` owns in-flight message state for the active session only — never the session list.
- TanStack Query owns the session list and any other server-state. Mutations invalidate the `['sessions']` key.
- Zustand owns `activeSessionId` and nothing else. Sidebar and ChatWindow both subscribe.
- The client **never** sends the full message history. The server loads it from Supabase using `sessionId` + the new message.
- Switching sessions remounts `<ChatWindow key={sessionId} />` so `useChat` state cannot leak.

---

## 4. Persistence Layer (Supabase)

```sql
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
create policy "user owns sessions" on chat_sessions for all using (auth.uid() = user_id);

-- chat_messages
create table chat_messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references chat_sessions on delete cascade not null,
  user_id uuid references auth.users not null,
  role text check (role in ('user','assistant','tool')) not null,
  parts jsonb not null,       -- AI SDK UIMessage.parts verbatim
  created_at timestamptz default now()
);
alter table chat_messages enable row level security;
create policy "user owns messages" on chat_messages for all using (auth.uid() = user_id);

create index on chat_messages(session_id, created_at);
```

**Decisions:**
- `parts jsonb` stores `UIMessage.parts` array verbatim — no custom mapping layer.
- `model` lives on the session, so each chat can use a different provider/model.
- Cascade delete on `chat_messages.session_id` — deleting a session deletes its messages.
- `updated_at` is bumped in the API route on every assistant response, used to sort sidebar "recent first."

---

## 5. API Layer (Next.js Route Handlers)

### 5.1 Streaming route — `POST /api/chat`

```ts
// app/api/chat/route.ts
import { convertToModelMessages, streamText, type UIMessage } from 'ai'
import { createClient } from '@/lib/supabase/server'
// No registry import — AI Gateway is default provider in ai v6

export const maxDuration = 60

export async function POST(req: Request) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return new Response('Unauthorized', { status: 401 })

  const { message, sessionId }:
    { message: UIMessage; sessionId: string } = await req.json()

  // Save incoming user message
  await supabase.from('chat_messages').insert({
    session_id: sessionId,
    user_id: user.id,
    role: 'user',
    parts: message.parts,
  })

  // Load session metadata + message history
  const [{ data: session }, { data: history }] = await Promise.all([
    supabase.from('chat_sessions').select('model').eq('id', sessionId).single(),
    supabase.from('chat_messages')
      .select('role, parts')
      .eq('session_id', sessionId)
      .order('created_at')
      .limit(100),
  ])

  const messages: UIMessage[] = (history ?? []).map(r => ({
    id: crypto.randomUUID(),
    role: r.role as UIMessage['role'],
    parts: r.parts,
  }))

  const result = streamText({
    model: session!.model, // Gateway routes 'anthropic/...', 'openai/...' etc.
    messages: convertToModelMessages(messages),
  })

  return result.toUIMessageStreamResponse({
    onFinish: async ({ responseMessage }) => {
      await Promise.all([
        supabase.from('chat_messages').insert({
          session_id: sessionId,
          user_id: user.id,
          role: 'assistant',
          parts: responseMessage.parts,
        }),
        supabase.from('chat_sessions')
          .update({ updated_at: new Date().toISOString() })
          .eq('id', sessionId),
      ])
    },
  })
}
```

**AI Gateway (no registry file needed):**

AI SDK v6 uses Vercel AI Gateway as the default provider. Pass model strings directly — no per-provider SDK installs required. Authenticate via `vercel env pull .env.local` (OIDC, preferred) or a manual API key from the Vercel dashboard.

```ts
// model strings route through Gateway automatically:
// 'anthropic/claude-sonnet-4.6'
// 'openai/gpt-4.1'
// 'google/gemini-2.5-pro'
```

### 5.2 Session CRUD — `/api/sessions`

| Verb     | Path                  | Purpose                                   |
|----------|-----------------------|-------------------------------------------|
| `GET`    | `/api/sessions`        | List user's sessions, `updated_at desc`   |
| `POST`   | `/api/sessions`        | Create new session, returns `{ id }`      |
| `PATCH`  | `/api/sessions/[id]`   | Rename `title`                            |
| `DELETE` | `/api/sessions/[id]`   | Delete session (cascades messages)        |
| `GET`    | `/api/sessions/[id]/messages` | Load full history for a session    |

All routes call `supabase.auth.getUser()` and return 401 if missing — RLS is a safety net, not the only check.

### 5.3 Auto-titling

After the **first** assistant response saves successfully, kick off (don't `await`):

```ts
generateText({
  model: registry.languageModel('anthropic/claude-haiku-4.5'),
  prompt: `Summarise this user message in <=6 words as a chat title:\n${firstUserText}`,
}).then(({ text }) =>
  supabase.from('chat_sessions').update({ title: text.trim() }).eq('id', sessionId)
)
```

Detect "first response" by checking message count on the session before save.

---

## 6. Data Layer (TanStack Query)

```ts
// lib/chat/queries.ts
export function useSessions() {
  return useQuery({
    queryKey: ['sessions'],
    queryFn: () => fetch('/api/sessions').then(r => r.json()),
  })
}

export function useSessionMessages(sessionId: string | null) {
  return useQuery({
    queryKey: ['messages', sessionId],
    queryFn: () => fetch(`/api/sessions/${sessionId}/messages`).then(r => r.json()),
    enabled: !!sessionId,
  })
}

export function useCreateSession() {
  const qc = useQueryClient()
  const setActive = useChatStore(s => s.setActiveSession)
  return useMutation({
    mutationFn: (model: string) =>
      fetch('/api/sessions', {
        method: 'POST',
        body: JSON.stringify({ model }),
      }).then(r => r.json()),
    onSuccess: (session) => {
      qc.invalidateQueries({ queryKey: ['sessions'] })
      setActive(session.id)
    },
  })
}

export function useDeleteSession() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) =>
      fetch(`/api/sessions/${id}`, { method: 'DELETE' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sessions'] }),
  })
}

export function useRenameSession() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, title }: { id: string; title: string }) =>
      fetch(`/api/sessions/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ title }),
      }),
    onSettled: () => qc.invalidateQueries({ queryKey: ['sessions'] }),
  })
}
```

---

## 7. Chat Hook Layer (Zustand + useChat)

```ts
// lib/chat/store.ts
import { create } from 'zustand'

interface ChatStore {
  activeSessionId: string | null
  setActiveSession: (id: string | null) => void
}

export const useChatStore = create<ChatStore>((set) => ({
  activeSessionId: null,
  setActiveSession: (id) => set({ activeSessionId: id }),
}))
```

```tsx
// components/chat/ChatWindow.tsx
'use client'
import { useChat } from '@ai-sdk/react'
import { DefaultChatTransport } from 'ai'
import { useChatStore } from '@/lib/chat/store'
import { useSessionMessages } from '@/lib/chat/queries'

export function ChatWindow() {
  const sessionId = useChatStore(s => s.activeSessionId)
  if (!sessionId) return <EmptyState />
  return <ChatWindowInner key={sessionId} sessionId={sessionId} />
  // key={} forces remount on session switch — no state bleed
}

function ChatWindowInner({ sessionId }: { sessionId: string }) {
  const { data: initialMessages, isLoading } = useSessionMessages(sessionId)
  if (isLoading) return <LoadingSkeleton />

  const { messages, sendMessage, status } = useChat({
    id: sessionId,
    messages: initialMessages ?? [],
    transport: new DefaultChatTransport({
      api: '/api/chat',
      body: { sessionId },
    }),
  })

  return (
    <div className="flex flex-col h-full">
      <MessageList messages={messages} status={status} />
      <ChatInput onSubmit={(text) => sendMessage({ text })} disabled={status === 'streaming'} />
    </div>
  )
}
```

---

## 8. UI Layer (Component Structure)

```
components/chat/
  ChatLayout.tsx          # sidebar + main pane split (CSS grid)
  SessionSidebar.tsx      # session list, new-chat button
  SessionItem.tsx         # row with title, context menu (rename / delete)
  ChatWindow.tsx          # outer wrapper with key={sessionId}
  ChatWindowInner.tsx     # mounts useChat, renders messages + input
  MessageList.tsx         # virtualized list, auto-scroll on new message
  MessageBubble.tsx       # role-aware bubble, renders UIMessage.parts
  StreamingIndicator.tsx  # pulsing dots while status === 'streaming'
  ChatInput.tsx           # textarea with TanStack Form, submit on Enter
  EmptyState.tsx          # shown when activeSessionId is null
  LoadingSkeleton.tsx     # shown while initialMessages load
```

### 8.1 MessageBubble (renders typed parts via AI Elements)

**Default renderer: AI Elements** (`@ai-sdk/elements`) — a streaming-aware component set built for AI SDK v6 message parts. It handles text/code/reasoning safely (escaping, sanitization, streaming chunk reconciliation) and reduces the surface area where teams hand-roll edge cases.

AI SDK v6 uses **typed tool parts** (`tool-<toolName>`) instead of the removed `tool-invocation` type. Use `isToolUIPart` as a generic catch-all when you don't want to enumerate every tool.

```tsx
import { isToolUIPart, type UIMessage } from 'ai'
import { Response, Reasoning } from '@ai-sdk/elements'

function MessageBubble({ message }: { message: UIMessage }) {
  return (
    <div className={message.role === 'user' ? 'user-bubble' : 'ai-bubble'}>
      {message.parts.map((part, i) => {
        if (part.type === 'text') return <Response key={i}>{part.text}</Response>
        if (part.type === 'reasoning') return <Reasoning key={i}>{part.text}</Reasoning>
        if (isToolUIPart(part)) return <ToolCallBlock key={part.toolCallId} part={part} />
        return null
      })}
    </div>
  )
}
```

`ToolCallBlock` should branch on `part.state` (`input-streaming` | `input-available` | `output-available` | `output-error`) before reading `part.input` or `part.output` — typed tool parts only expose those properties in matching states.

> **Override path (rare):** If a project has a unified team-wide rich-text renderer used outside chat (e.g., on blog/docs surfaces), substituting the text-part renderer with the team renderer is acceptable. That substitution is a separate, opt-in spec — do not mix the two in the same surface.

### 8.2 Auto-scroll

Inside `MessageList`, use a ref to the scroll container + an effect that scrolls to bottom on every new message or every chunk during streaming. Don't auto-scroll if the user has scrolled up — track scroll position and only auto-scroll when within ~50px of the bottom (mimics ChatGPT behaviour).

### 8.3 New chat flow

1. User clicks "New Chat" → `useCreateSession()` mutation fires.
2. On success, `activeSessionId` is set → ChatWindow remounts with the new session ID.
3. User types first message → `sendMessage` → `POST /api/chat`.
4. After first assistant response, auto-title kicks off → session title updates in sidebar via Query invalidation.

---

## 9. Tool Use Extension (opt-in)

To add tool calling, extend `streamText` in `/api/chat`:

```ts
import { tool, stepCountIs } from 'ai'
import { z } from 'zod'

const result = streamText({
  model: registry.languageModel(session!.model),
  messages: convertToModelMessages(messages),
  tools: {
    search: tool({
      description: 'Search the web',
      inputSchema: z.object({ query: z.string() }),
      execute: async ({ query }) => { /* ... */ },
    }),
  },
  stopWhen: stepCountIs(5), // allow multi-step tool loops
})
```

Client renders `tool-invocation` parts automatically via the existing `MessageBubble` switch — no client changes needed.

> **Note on API churn:** AI SDK has migrated `maxSteps → stopWhen: stepCountIs(N)` between v4 and v5. Always cross-check the canonical reference at <https://ai-sdk.dev/docs> before copying snippets — the layer boundaries in this doc are stable; the function names will shift.

---

## 10. What's intentionally NOT in this spec

The following subsystems get their own specs in subsequent brainstorming cycles:

| Subsystem | Why deferred |
|---|---|
| **Authentication (Supabase Auth)** | Affects every project, not just chatbot — gets its own reference. |
| **SEO + Core Web Vitals** | Cross-cutting concern, irrelevant inside the chat surface (which is usually authenticated/no-index). |
| **Loading performance** | Project-wide concern. |
| **Rich-text rendering on non-chat surfaces** | Blog, docs, and comments need their own rendering pipeline. Inside chat, AI Elements is used (see Section 8.1). |
| **File attachments / image input in chat** | Out of scope for v1. |
| **Streaming reasoning / thinking blocks UI polish** | UI polish, not architecture. |
| **Rate limiting / abuse prevention** | Cross-cutting concern. |

---

## 11. Open questions

1. **Anonymous chat?** Current design requires auth. If guest chat is needed later, add a `device_id` column and a `guest` RLS path.
2. **Message editing / branching (like ChatGPT's "edit message")?** Not in v1. Would require a `parent_id` column on `chat_messages`.
3. **Provider failover via Vercel AI Gateway?** The provider registry pattern is compatible; flip `registry.languageModel('anthropic/claude-…')` to use Gateway model strings later.

---

## 12. Next step

After user review of this spec, invoke `superpowers:writing-plans` to produce the phased implementation plan.
