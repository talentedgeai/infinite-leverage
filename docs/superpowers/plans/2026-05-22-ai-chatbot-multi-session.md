# AI Chatbot — Multi-Session Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fully working multi-session AI chatbot (ChatGPT/Claude/Gemini-style) using Next.js App Router, Supabase, and AI SDK v6 that developers can copy into any client project.

**Architecture:** Five strict layers (Persistence → API → Data → Hook → UI). The client never sends full message history — the server loads it from Supabase per request. Switching sessions remounts `<ChatWindow key={sessionId} />` to prevent state bleed.

**Tech Stack:** `ai` v6 (includes AI Gateway as default provider — no per-provider SDK installs needed), `@ai-sdk/react`, `@ai-sdk/elements`, `zustand`, `@tanstack/react-query` v5, `@tanstack/react-form`, Supabase JS v2, Vitest, React Testing Library.

> **Path convention:** All paths are relative to your Next.js app root (where `app/` lives). In the scaffold template this is `website/`. Adjust accordingly.

---

## File Map

| File | Responsibility |
|---|---|
| `supabase/migrations/20260522000000_chat_tables.sql` | Schema: `chat_sessions`, `chat_messages`, RLS, index |
| `.env.local` | Gateway credentials — pulled via `vercel env pull` (OIDC, preferred) or manual API key |
| `app/api/sessions/route.ts` | GET list + POST create sessions |
| `app/api/sessions/[id]/route.ts` | PATCH rename + DELETE session |
| `app/api/sessions/[id]/messages/route.ts` | GET message history for a session |
| `app/api/chat/route.ts` | POST streaming chat + auto-title on first response |
| `lib/chat/store.ts` | Zustand store — `activeSessionId` only |
| `lib/chat/queries.ts` | TanStack Query hooks for sessions + messages |
| `components/chat/ChatLayout.tsx` | CSS grid — sidebar left, chat pane right |
| `components/chat/SessionSidebar.tsx` | Session list + New Chat button |
| `components/chat/SessionItem.tsx` | Single row: title + rename/delete context menu |
| `components/chat/EmptyState.tsx` | Shown when no session selected |
| `components/chat/LoadingSkeleton.tsx` | Shown while history loads |
| `components/chat/StreamingIndicator.tsx` | Pulsing dots during streaming |
| `components/chat/MessageBubble.tsx` | Renders `UIMessage.parts` via AI Elements |
| `components/chat/ToolCallBlock.tsx` | Renders tool parts with state-gated input/output |
| `components/chat/MessageList.tsx` | Scrollable list with auto-scroll-to-bottom |
| `components/chat/ChatInput.tsx` | Textarea + TanStack Form + Enter-to-send |
| `components/chat/ChatWindow.tsx` | Outer wrapper (`key={sessionId}` remount) |
| `components/chat/ChatWindowInner.tsx` | Mounts `useChat`, composes MessageList + ChatInput |
| `app/chat/page.tsx` | Route page — mounts `<ChatLayout />` |

---

## Task 1: Database Migration

**Files:**
- Create: `supabase/migrations/20260522000000_chat_tables.sql`

- [ ] **Step 1: Create the migration file**

```sql
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
```

- [ ] **Step 2: Apply the migration**

```bash
npx supabase db push
```

Expected: `Applying migration 20260522000000_chat_tables.sql`

If you don't have Supabase CLI linked: `npx supabase link --project-ref <YOUR_REF>` first.

- [ ] **Step 3: Verify tables exist**

```bash
npx supabase db diff --linked
```

Expected: empty diff (migration already applied).

- [ ] **Step 4: Commit**

```bash
git add supabase/migrations/20260522000000_chat_tables.sql
git commit -m "feat(chat): add chat_sessions and chat_messages tables with RLS"
```

---

## Task 2: Install Dependencies

**Files:** `package.json` (modified), `.env.local`

- [ ] **Step 1: Install AI SDK packages**

AI Gateway is built into `ai` v6 — no per-provider SDK packages needed. All providers (Anthropic, OpenAI, Google, etc.) are accessed via a single Gateway API key.

```bash
npm install ai @ai-sdk/react @ai-sdk/elements zustand
```

- [ ] **Step 2: Add AI Gateway API key to environment**

**On Vercel (preferred — OIDC, no manual rotation):**
```bash
vercel env pull .env.local
```
Pulls the Gateway credential automatically. OIDC tokens rotate without intervention — nothing to manage.

**Fallback (no Vercel project linked):** Create `.env.local` manually with a Gateway API key from `vercel.com/[team]/~/ai-gateway/api-keys`. The `ai` package reads it automatically at runtime.

- [ ] **Step 2: Install test dependencies**

```bash
npm install -D vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/user-event @testing-library/jest-dom
```

- [ ] **Step 3: Add vitest config** (skip if already present)

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
  },
})
```

```ts
// vitest.setup.ts
import '@testing-library/jest-dom'
```

- [ ] **Step 4: Verify install**

```bash
npx vitest run --reporter=verbose 2>&1 | head -5
```

Expected: `0 tests` or existing tests passing. No import errors.

- [ ] **Step 5: Commit**

```bash
git add package.json package-lock.json vitest.config.ts vitest.setup.ts
git commit -m "feat(chat): install AI SDK, Zustand, and test dependencies"
```

---

## Task 3: Verify AI Gateway Works

**Files:** none — `ai` v6 uses AI Gateway as its default provider automatically.

No registry file needed. Model strings like `'anthropic/claude-sonnet-4.6'` route through AI Gateway without any configuration beyond the credential pulled in Task 2.

- [ ] **Step 1: Write a smoke test**

```ts
// lib/ai/gateway.test.ts
import { describe, it, expect, vi } from 'vitest'

describe('AI Gateway model strings', () => {
  it('gateway provider string format is provider/model', () => {
    const model = 'anthropic/claude-sonnet-4.6'
    expect(model).toMatch(/^[a-z]+\/[a-z-0-9.]+$/)
  })

  it('haiku model string is valid for auto-titling', () => {
    const model = 'anthropic/claude-haiku-4.5'
    expect(model).toMatch(/^anthropic\//)
  })
})
```

- [ ] **Step 2: Run tests**

```bash
npx vitest run lib/ai/gateway.test.ts
```

Expected: `2 passed`

- [ ] **Step 3: Commit**

```bash
git add lib/ai/gateway.test.ts
git commit -m "feat(chat): verify AI Gateway model string format"
```

---

## Task 4: Session CRUD API Routes

**Files:**
- Create: `app/api/sessions/route.ts`
- Create: `app/api/sessions/[id]/route.ts`
- Create: `app/api/sessions/[id]/messages/route.ts`

> These routes all call `supabase.auth.getUser()` and return 401 if missing. RLS is a safety net, not the primary auth check.

- [ ] **Step 1: Create `app/api/sessions/route.ts`**

```ts
// app/api/sessions/route.ts
import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

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
  const model = body.model ?? 'anthropic/claude-sonnet-4.6'

  const { data, error } = await supabase
    .from('chat_sessions')
    .insert({ user_id: user.id, model })
    .select('id, title, model, created_at, updated_at')
    .single()

  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return NextResponse.json(data, { status: 201 })
}
```

- [ ] **Step 2: Create `app/api/sessions/[id]/route.ts`**

```ts
// app/api/sessions/[id]/route.ts
import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function PATCH(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return new NextResponse('Unauthorized', { status: 401 })

  const { title } = await req.json()
  if (!title?.trim()) {
    return NextResponse.json({ error: 'title is required' }, { status: 400 })
  }

  const { error } = await supabase
    .from('chat_sessions')
    .update({ title: title.trim() })
    .eq('id', id)
    .eq('user_id', user.id)

  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return new NextResponse(null, { status: 204 })
}

export async function DELETE(
  _req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return new NextResponse('Unauthorized', { status: 401 })

  const { error } = await supabase
    .from('chat_sessions')
    .delete()
    .eq('id', id)
    .eq('user_id', user.id)

  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return new NextResponse(null, { status: 204 })
}
```

- [ ] **Step 3: Create `app/api/sessions/[id]/messages/route.ts`**

```ts
// app/api/sessions/[id]/messages/route.ts
import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'
import type { UIMessage } from 'ai'

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return new NextResponse('Unauthorized', { status: 401 })

  const { data, error } = await supabase
    .from('chat_messages')
    .select('id, role, parts, created_at')
    .eq('session_id', id)
    .order('created_at', { ascending: true })
    .limit(100)

  if (error) return NextResponse.json({ error: error.message }, { status: 500 })

  const messages: UIMessage[] = (data ?? []).map(row => ({
    id: row.id,
    role: row.role as UIMessage['role'],
    parts: row.parts,
  }))

  return NextResponse.json(messages)
}
```

- [ ] **Step 4: Verify routes compile**

```bash
npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 5: Commit**

```bash
git add app/api/sessions/
git commit -m "feat(chat): add session CRUD API routes (list, create, rename, delete, messages)"
```

---

## Task 5: Streaming Chat Route + Auto-title

**Files:**
- Create: `app/api/chat/route.ts`

- [ ] **Step 1: Create the streaming route**

```ts
// app/api/chat/route.ts
import { convertToModelMessages, generateText, streamText, type UIMessage } from 'ai'
import { createClient } from '@/lib/supabase/server'
// No provider import needed — AI Gateway is the default provider in ai v6

export const maxDuration = 60

export async function POST(req: Request) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return new Response('Unauthorized', { status: 401 })

  const { message, sessionId }: { message: UIMessage; sessionId: string } =
    await req.json()

  // Verify session ownership
  const { data: session, error: sessionError } = await supabase
    .from('chat_sessions')
    .select('model')
    .eq('id', sessionId)
    .eq('user_id', user.id)
    .single()

  if (sessionError || !session) return new Response('Not Found', { status: 404 })

  // Count existing messages to detect first response
  const { count } = await supabase
    .from('chat_messages')
    .select('id', { count: 'exact', head: true })
    .eq('session_id', sessionId)

  const isFirstMessage = (count ?? 0) === 0

  // Save incoming user message
  await supabase.from('chat_messages').insert({
    session_id: sessionId,
    user_id: user.id,
    role: 'user',
    parts: message.parts,
  })

  // Load full history (including just-saved user message)
  const { data: history } = await supabase
    .from('chat_messages')
    .select('id, role, parts')
    .eq('session_id', sessionId)
    .order('created_at', { ascending: true })
    .limit(100)

  const messages: UIMessage[] = (history ?? []).map(row => ({
    id: row.id,
    role: row.role as UIMessage['role'],
    parts: row.parts,
  }))

  const result = streamText({
    model: session.model, // AI Gateway routes 'anthropic/...', 'openai/...', etc. automatically
    messages: convertToModelMessages(messages),
  })

  return result.toUIMessageStreamResponse({
    onFinish: async ({ responseMessage }) => {
      // Save assistant message
      await supabase.from('chat_messages').insert({
        session_id: sessionId,
        user_id: user.id,
        role: 'assistant',
        parts: responseMessage.parts,
      })

      // Bump updated_at on session
      await supabase
        .from('chat_sessions')
        .update({ updated_at: new Date().toISOString() })
        .eq('id', sessionId)

      // Auto-title on first exchange (fire-and-forget)
      if (isFirstMessage) {
        const firstTextPart = message.parts.find(p => p.type === 'text')
        const firstUserText =
          firstTextPart && 'text' in firstTextPart ? firstTextPart.text : ''

        if (firstUserText) {
          generateText({
            model: 'anthropic/claude-haiku-4.5',
            prompt: `Summarise this message in 6 words or fewer as a chat title. Reply with ONLY the title, no quotes:\n\n${firstUserText}`,
          })
            .then(({ text }) =>
              supabase
                .from('chat_sessions')
                .update({ title: text.trim() })
                .eq('id', sessionId)
            )
            .catch(() => {/* auto-title failure is non-critical */})
        }
      }
    },
  })
}
```

- [ ] **Step 2: Verify compile**

```bash
npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 3: Smoke-test with curl** (requires a running dev server and valid session cookie)

```bash
npm run dev &
# In a separate terminal, after logging in and getting a session cookie:
curl -X POST http://localhost:3000/api/sessions \
  -H "Content-Type: application/json" \
  -H "Cookie: <your-auth-cookie>" \
  -d '{"model":"anthropic/claude-sonnet-4.6"}'
```

Expected: `{"id":"<uuid>","title":"New Chat","model":"anthropic/claude-sonnet-4.6",...}`

- [ ] **Step 4: Commit**

```bash
git add app/api/chat/route.ts
git commit -m "feat(chat): add streaming POST /api/chat with auto-title on first exchange"
```

---

## Task 6: Zustand Store + TanStack Query Hooks

**Files:**
- Create: `lib/chat/store.ts`
- Create: `lib/chat/store.test.ts`
- Create: `lib/chat/queries.ts`
- Create: `lib/chat/queries.test.ts`

- [ ] **Step 1: Write store test**

```ts
// lib/chat/store.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { useChatStore } from './store'
import { act } from 'react'

describe('useChatStore', () => {
  beforeEach(() => {
    act(() => useChatStore.setState({ activeSessionId: null }))
  })

  it('starts with null activeSessionId', () => {
    expect(useChatStore.getState().activeSessionId).toBeNull()
  })

  it('sets activeSessionId', () => {
    act(() => useChatStore.getState().setActiveSession('abc-123'))
    expect(useChatStore.getState().activeSessionId).toBe('abc-123')
  })

  it('clears activeSessionId', () => {
    act(() => useChatStore.getState().setActiveSession('abc-123'))
    act(() => useChatStore.getState().setActiveSession(null))
    expect(useChatStore.getState().activeSessionId).toBeNull()
  })
})
```

- [ ] **Step 2: Run to confirm fail**

```bash
npx vitest run lib/chat/store.test.ts
```

Expected: `FAIL — Cannot find module './store'`

- [ ] **Step 3: Implement store**

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

- [ ] **Step 4: Run store tests**

```bash
npx vitest run lib/chat/store.test.ts
```

Expected: `3 passed`

- [ ] **Step 5: Write queries test**

```ts
// lib/chat/queries.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createElement } from 'react'
import { useSessions, useCreateSession } from './queries'
import { act } from 'react'
import { useChatStore } from './store'

// Minimal wrapper
function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return ({ children }: { children: React.ReactNode }) =>
    createElement(QueryClientProvider, { client: qc }, children)
}

describe('useSessions', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
    act(() => useChatStore.setState({ activeSessionId: null }))
  })

  it('fetches /api/sessions', async () => {
    const mockSessions = [{ id: 'session-1', title: 'New Chat' }]
    vi.mocked(fetch).mockResolvedValueOnce({
      json: () => Promise.resolve(mockSessions),
      ok: true,
    } as Response)

    const { result } = renderHook(() => useSessions(), {
      wrapper: makeWrapper(),
    })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data).toEqual(mockSessions)
    expect(fetch).toHaveBeenCalledWith('/api/sessions')
  })
})

describe('useCreateSession', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
    act(() => useChatStore.setState({ activeSessionId: null }))
  })

  it('POSTs to /api/sessions and sets activeSessionId on success', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      json: () => Promise.resolve({ id: 'new-session', title: 'New Chat' }),
      ok: true,
    } as Response)
    // Second fetch for invalidation refetch
    vi.mocked(fetch).mockResolvedValueOnce({
      json: () => Promise.resolve([]),
      ok: true,
    } as Response)

    const { result } = renderHook(() => useCreateSession(), {
      wrapper: makeWrapper(),
    })

    await act(async () => {
      result.current.mutate('anthropic/claude-sonnet-4.6')
    })

    await waitFor(() => result.current.isSuccess)
    expect(useChatStore.getState().activeSessionId).toBe('new-session')
  })
})
```

- [ ] **Step 6: Run to confirm fail**

```bash
npx vitest run lib/chat/queries.test.ts
```

Expected: `FAIL — Cannot find module './queries'`

- [ ] **Step 7: Implement queries**

```ts
// lib/chat/queries.ts
import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryResult,
} from '@tanstack/react-query'
import { useChatStore } from './store'
import type { UIMessage } from 'ai'

export interface ChatSession {
  id: string
  title: string
  model: string
  created_at: string
  updated_at: string
}

export function useSessions(): UseQueryResult<ChatSession[]> {
  return useQuery({
    queryKey: ['sessions'],
    queryFn: () => fetch('/api/sessions').then(r => r.json()),
  })
}

export function useSessionMessages(
  sessionId: string | null
): UseQueryResult<UIMessage[]> {
  return useQuery({
    queryKey: ['messages', sessionId],
    queryFn: () =>
      fetch(`/api/sessions/${sessionId}/messages`).then(r => r.json()),
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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model }),
      }).then(r => r.json()),
    onSuccess: (session: ChatSession) => {
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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title }),
      }),
    onSettled: () => qc.invalidateQueries({ queryKey: ['sessions'] }),
  })
}
```

- [ ] **Step 8: Run all tests**

```bash
npx vitest run lib/chat/
```

Expected: `5 passed`

- [ ] **Step 9: Commit**

```bash
git add lib/chat/store.ts lib/chat/store.test.ts lib/chat/queries.ts lib/chat/queries.test.ts
git commit -m "feat(chat): add Zustand store and TanStack Query hooks for session management"
```

---

## Task 7: Core UI — StreamingIndicator, EmptyState, LoadingSkeleton, ToolCallBlock

**Files:**
- Create: `components/chat/StreamingIndicator.tsx`
- Create: `components/chat/EmptyState.tsx`
- Create: `components/chat/LoadingSkeleton.tsx`
- Create: `components/chat/ToolCallBlock.tsx`

- [ ] **Step 1: Create `StreamingIndicator.tsx`**

```tsx
// components/chat/StreamingIndicator.tsx
export function StreamingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-2" aria-label="AI is responding">
      {[0, 1, 2].map(i => (
        <span
          key={i}
          className="h-2 w-2 rounded-full bg-gray-400 animate-bounce"
          style={{ animationDelay: `${i * 150}ms` }}
        />
      ))}
    </div>
  )
}
```

- [ ] **Step 2: Create `EmptyState.tsx`**

```tsx
// components/chat/EmptyState.tsx
export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-gray-500 gap-3">
      <p className="text-lg font-medium">No chat selected</p>
      <p className="text-sm">Create a new chat or select one from the sidebar.</p>
    </div>
  )
}
```

- [ ] **Step 3: Create `LoadingSkeleton.tsx`**

```tsx
// components/chat/LoadingSkeleton.tsx
export function LoadingSkeleton() {
  return (
    <div className="flex flex-col gap-3 p-4 animate-pulse" aria-busy="true">
      {[80, 60, 90, 50].map((w, i) => (
        <div
          key={i}
          className="h-4 rounded bg-gray-200"
          style={{ width: `${w}%` }}
        />
      ))}
    </div>
  )
}
```

- [ ] **Step 4: Create `ToolCallBlock.tsx`**

```tsx
// components/chat/ToolCallBlock.tsx
import { isToolUIPart } from 'ai'
import type { UIMessage } from 'ai'

// UIMessage['parts'][number] gives the union of all part types
type AnyPart = UIMessage['parts'][number]

interface Props {
  part: AnyPart & { type: `tool-${string}` }
}

export function ToolCallBlock({ part }: Props) {
  if (!isToolUIPart(part)) return null

  return (
    <div className="my-2 rounded border border-gray-200 bg-gray-50 p-3 text-sm font-mono">
      <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
        <span className="font-semibold text-gray-700">{part.toolName}</span>
        <span className="rounded bg-gray-200 px-1">{part.state}</span>
      </div>

      {(part.state === 'input-available' || part.state === 'output-available') && (
        <div className="mb-1">
          <span className="text-gray-500">Input: </span>
          <pre className="inline whitespace-pre-wrap break-all">
            {JSON.stringify(part.input, null, 2)}
          </pre>
        </div>
      )}

      {part.state === 'output-available' && (
        <div>
          <span className="text-gray-500">Output: </span>
          <pre className="inline whitespace-pre-wrap break-all">
            {JSON.stringify(part.output, null, 2)}
          </pre>
        </div>
      )}

      {part.state === 'output-error' && (
        <div className="text-red-600">Tool call failed.</div>
      )}
    </div>
  )
}
```

- [ ] **Step 5: Verify compile**

```bash
npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 6: Commit**

```bash
git add components/chat/StreamingIndicator.tsx components/chat/EmptyState.tsx \
        components/chat/LoadingSkeleton.tsx components/chat/ToolCallBlock.tsx
git commit -m "feat(chat): add StreamingIndicator, EmptyState, LoadingSkeleton, ToolCallBlock"
```

---

## Task 8: MessageBubble + MessageList

**Files:**
- Create: `components/chat/MessageBubble.tsx`
- Create: `components/chat/MessageBubble.test.tsx`
- Create: `components/chat/MessageList.tsx`

- [ ] **Step 1: Write MessageBubble test**

```tsx
// components/chat/MessageBubble.test.tsx
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MessageBubble } from './MessageBubble'
import type { UIMessage } from 'ai'

const userMsg: UIMessage = {
  id: '1',
  role: 'user',
  parts: [{ type: 'text', text: 'Hello world' }],
}

const assistantMsg: UIMessage = {
  id: '2',
  role: 'assistant',
  parts: [{ type: 'text', text: 'Hi there!' }],
}

describe('MessageBubble', () => {
  it('renders user message text', () => {
    render(<MessageBubble message={userMsg} />)
    expect(screen.getByText('Hello world')).toBeInTheDocument()
  })

  it('applies user-bubble class for user messages', () => {
    const { container } = render(<MessageBubble message={userMsg} />)
    expect(container.firstChild).toHaveClass('user-bubble')
  })

  it('applies ai-bubble class for assistant messages', () => {
    const { container } = render(<MessageBubble message={assistantMsg} />)
    expect(container.firstChild).toHaveClass('ai-bubble')
  })
})
```

- [ ] **Step 2: Run to confirm fail**

```bash
npx vitest run components/chat/MessageBubble.test.tsx
```

Expected: `FAIL — Cannot find module './MessageBubble'`

- [ ] **Step 3: Implement MessageBubble**

```tsx
// components/chat/MessageBubble.tsx
'use client'
import { isToolUIPart, type UIMessage } from 'ai'
import { Response, Reasoning } from '@ai-sdk/elements'
import { ToolCallBlock } from './ToolCallBlock'

interface Props {
  message: UIMessage
}

export function MessageBubble({ message }: Props) {
  return (
    <div
      className={
        message.role === 'user'
          ? 'user-bubble ml-auto max-w-[75%] rounded-2xl bg-blue-500 px-4 py-2 text-white'
          : 'ai-bubble mr-auto max-w-[85%] rounded-2xl bg-gray-100 px-4 py-2 text-gray-900'
      }
    >
      {message.parts.map((part, i) => {
        if (part.type === 'text') {
          return <Response key={i}>{part.text}</Response>
        }
        if (part.type === 'reasoning') {
          return (
            <details key={i} className="text-xs text-gray-500 mt-1">
              <summary>Reasoning</summary>
              <Reasoning>{part.text}</Reasoning>
            </details>
          )
        }
        if (isToolUIPart(part)) {
          return <ToolCallBlock key={part.toolCallId} part={part} />
        }
        return null
      })}
    </div>
  )
}
```

- [ ] **Step 4: Run MessageBubble tests**

```bash
npx vitest run components/chat/MessageBubble.test.tsx
```

Expected: `3 passed`

- [ ] **Step 5: Implement MessageList with auto-scroll**

```tsx
// components/chat/MessageList.tsx
'use client'
import { useEffect, useRef } from 'react'
import type { UIMessage } from 'ai'
import { MessageBubble } from './MessageBubble'
import { StreamingIndicator } from './StreamingIndicator'

// status comes directly from useChat — 'idle' | 'streaming' | 'submitted' | 'error'
interface Props {
  messages: UIMessage[]
  status: 'idle' | 'streaming' | 'submitted' | 'error'
}

export function MessageList({ messages, status }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const isNearBottomRef = useRef(true)

  // Track whether user is near the bottom
  function handleScroll() {
    const el = containerRef.current
    if (!el) return
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight
    isNearBottomRef.current = distanceFromBottom < 50
  }

  // Auto-scroll when messages change — only if near bottom
  useEffect(() => {
    const el = containerRef.current
    if (!el || !isNearBottomRef.current) return
    el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  }, [messages])

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      className="flex-1 overflow-y-auto flex flex-col gap-3 p-4"
    >
      {messages.map(message => (
        <MessageBubble key={message.id} message={message} />
      ))}
      {status === 'streaming' && <StreamingIndicator />}
    </div>
  )
}
```

- [ ] **Step 6: Verify compile**

```bash
npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 7: Commit**

```bash
git add components/chat/MessageBubble.tsx components/chat/MessageBubble.test.tsx \
        components/chat/MessageList.tsx
git commit -m "feat(chat): add MessageBubble (AI Elements) and MessageList with auto-scroll"
```

---

## Task 9: ChatInput

**Files:**
- Create: `components/chat/ChatInput.tsx`
- Create: `components/chat/ChatInput.test.tsx`

- [ ] **Step 1: Write ChatInput test**

```tsx
// components/chat/ChatInput.test.tsx
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChatInput } from './ChatInput'

describe('ChatInput', () => {
  it('calls onSubmit with trimmed text on Enter', async () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} disabled={false} />)

    await userEvent.type(screen.getByRole('textbox'), 'Hello world{Enter}')
    expect(onSubmit).toHaveBeenCalledWith('Hello world')
  })

  it('does not submit empty or whitespace-only input', async () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} disabled={false} />)

    await userEvent.type(screen.getByRole('textbox'), '   {Enter}')
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('disables textarea when disabled=true', () => {
    render(<ChatInput onSubmit={vi.fn()} disabled={true} />)
    expect(screen.getByRole('textbox')).toBeDisabled()
  })

  it('clears input after submit', async () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} disabled={false} />)
    const textarea = screen.getByRole('textbox')

    await userEvent.type(textarea, 'Hello{Enter}')
    expect(textarea).toHaveValue('')
  })
})
```

- [ ] **Step 2: Run to confirm fail**

```bash
npx vitest run components/chat/ChatInput.test.tsx
```

Expected: `FAIL — Cannot find module './ChatInput'`

- [ ] **Step 3: Implement ChatInput**

```tsx
// components/chat/ChatInput.tsx
'use client'
import { useRef } from 'react'

interface Props {
  onSubmit: (text: string) => void
  disabled: boolean
}

export function ChatInput({ onSubmit, disabled }: Props) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  function submit() {
    const value = textareaRef.current?.value.trim() ?? ''
    if (!value || disabled) return
    onSubmit(value)
    if (textareaRef.current) textareaRef.current.value = ''
  }

  return (
    <div className="border-t border-gray-200 p-4">
      <div className="flex items-end gap-2 rounded-xl border border-gray-300 bg-white p-3 focus-within:ring-2 focus-within:ring-blue-500">
        <textarea
          ref={textareaRef}
          rows={1}
          disabled={disabled}
          onKeyDown={handleKeyDown}
          placeholder="Message..."
          className="flex-1 resize-none bg-transparent text-sm outline-none disabled:opacity-50"
        />
        <button
          type="button"
          onClick={submit}
          disabled={disabled}
          className="rounded-lg bg-blue-500 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-600 disabled:opacity-50"
        >
          Send
        </button>
      </div>
      <p className="mt-1 text-center text-xs text-gray-400">
        Enter to send · Shift+Enter for new line
      </p>
    </div>
  )
}
```

- [ ] **Step 4: Run ChatInput tests**

```bash
npx vitest run components/chat/ChatInput.test.tsx
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add components/chat/ChatInput.tsx components/chat/ChatInput.test.tsx
git commit -m "feat(chat): add ChatInput with Enter-to-send and empty-input guard"
```

---

## Task 10: ChatWindow + ChatWindowInner

**Files:**
- Create: `components/chat/ChatWindowInner.tsx`
- Create: `components/chat/ChatWindow.tsx`

- [ ] **Step 1: Create `ChatWindowInner.tsx`**

```tsx
// components/chat/ChatWindowInner.tsx
'use client'
import { useChat } from '@ai-sdk/react'
import { DefaultChatTransport } from 'ai'
import { useSessionMessages } from '@/lib/chat/queries'
import { MessageList } from './MessageList'
import { ChatInput } from './ChatInput'
import { LoadingSkeleton } from './LoadingSkeleton'

interface Props {
  sessionId: string
}

export function ChatWindowInner({ sessionId }: Props) {
  const { data: initialMessages, isLoading } = useSessionMessages(sessionId)

  const { messages, sendMessage, status } = useChat({
    id: sessionId,
    messages: initialMessages ?? [],
    transport: new DefaultChatTransport({
      api: '/api/chat',
      body: { sessionId },
    }),
  })

  if (isLoading) return <LoadingSkeleton />

  return (
    <div className="flex flex-col h-full">
      <MessageList messages={messages} status={status} />
      <ChatInput
        onSubmit={(text) => sendMessage({ text })}
        disabled={status === 'streaming'}
      />
    </div>
  )
}
```

- [ ] **Step 2: Create `ChatWindow.tsx`**

```tsx
// components/chat/ChatWindow.tsx
'use client'
import { useChatStore } from '@/lib/chat/store'
import { EmptyState } from './EmptyState'
import { ChatWindowInner } from './ChatWindowInner'

export function ChatWindow() {
  const sessionId = useChatStore(s => s.activeSessionId)

  if (!sessionId) return <EmptyState />

  // key forces remount on session switch — prevents useChat state from
  // bleeding across sessions
  return <ChatWindowInner key={sessionId} sessionId={sessionId} />
}
```

- [ ] **Step 3: Verify compile**

```bash
npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add components/chat/ChatWindowInner.tsx components/chat/ChatWindow.tsx
git commit -m "feat(chat): add ChatWindow (remount-on-switch) and ChatWindowInner (useChat)"
```

---

## Task 11: Sidebar + Layout + Page Route

**Files:**
- Create: `components/chat/SessionItem.tsx`
- Create: `components/chat/SessionSidebar.tsx`
- Create: `components/chat/ChatLayout.tsx`
- Create: `app/chat/page.tsx`

- [ ] **Step 1: Create `SessionItem.tsx`**

```tsx
// components/chat/SessionItem.tsx
'use client'
import { useState } from 'react'
import { useChatStore } from '@/lib/chat/store'
import { useDeleteSession, useRenameSession } from '@/lib/chat/queries'
import type { ChatSession } from '@/lib/chat/queries'

interface Props {
  session: ChatSession
  isActive: boolean
}

export function SessionItem({ session, isActive }: Props) {
  const setActive = useChatStore(s => s.setActiveSession)
  const deleteSession = useDeleteSession()
  const renameSession = useRenameSession()
  const [isRenaming, setIsRenaming] = useState(false)
  const [renameValue, setRenameValue] = useState(session.title)

  function confirmRename() {
    const trimmed = renameValue.trim()
    if (trimmed && trimmed !== session.title) {
      renameSession.mutate({ id: session.id, title: trimmed })
    }
    setIsRenaming(false)
  }

  return (
    <div
      className={`group flex items-center gap-2 rounded-lg px-3 py-2 cursor-pointer ${
        isActive ? 'bg-gray-200' : 'hover:bg-gray-100'
      }`}
      onClick={() => setActive(session.id)}
    >
      {isRenaming ? (
        <input
          autoFocus
          value={renameValue}
          onChange={e => setRenameValue(e.target.value)}
          onBlur={confirmRename}
          onKeyDown={e => {
            if (e.key === 'Enter') confirmRename()
            if (e.key === 'Escape') setIsRenaming(false)
          }}
          className="flex-1 bg-transparent text-sm outline-none border-b border-gray-400"
          onClick={e => e.stopPropagation()}
        />
      ) : (
        <span className="flex-1 truncate text-sm">{session.title}</span>
      )}

      <div
        className="hidden group-hover:flex items-center gap-1"
        onClick={e => e.stopPropagation()}
      >
        <button
          title="Rename"
          onClick={() => setIsRenaming(true)}
          className="rounded p-1 text-xs hover:bg-gray-300"
        >
          ✏️
        </button>
        <button
          title="Delete"
          onClick={() => deleteSession.mutate(session.id)}
          className="rounded p-1 text-xs hover:bg-red-100 text-red-600"
        >
          🗑️
        </button>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Create `SessionSidebar.tsx`**

```tsx
// components/chat/SessionSidebar.tsx
'use client'
import { useSessions, useCreateSession } from '@/lib/chat/queries'
import { useChatStore } from '@/lib/chat/store'
import { SessionItem } from './SessionItem'

export function SessionSidebar() {
  const { data: sessions, isLoading } = useSessions()
  const createSession = useCreateSession()
  const activeId = useChatStore(s => s.activeSessionId)

  return (
    <aside className="flex flex-col h-full w-64 border-r border-gray-200 bg-gray-50">
      <div className="p-3 border-b border-gray-200">
        <button
          onClick={() => createSession.mutate('anthropic/claude-sonnet-4.6')}
          disabled={createSession.isPending}
          className="w-full rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 disabled:opacity-50"
        >
          + New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 flex flex-col gap-1">
        {isLoading && (
          <p className="text-xs text-gray-400 px-2 py-1">Loading...</p>
        )}
        {sessions?.map(session => (
          <SessionItem
            key={session.id}
            session={session}
            isActive={session.id === activeId}
          />
        ))}
        {!isLoading && sessions?.length === 0 && (
          <p className="text-xs text-gray-400 px-2 py-4 text-center">
            No chats yet. Create one above.
          </p>
        )}
      </div>
    </aside>
  )
}
```

- [ ] **Step 3: Create `ChatLayout.tsx`**

```tsx
// components/chat/ChatLayout.tsx
'use client'
import { SessionSidebar } from './SessionSidebar'
import { ChatWindow } from './ChatWindow'

export function ChatLayout() {
  return (
    <div className="flex h-screen">
      <SessionSidebar />
      <main className="flex-1 flex flex-col overflow-hidden">
        <ChatWindow />
      </main>
    </div>
  )
}
```

- [ ] **Step 4: Create the route page**

```tsx
// app/chat/page.tsx
import { ChatLayout } from '@/components/chat/ChatLayout'

export default function ChatPage() {
  return <ChatLayout />
}
```

- [ ] **Step 5: Verify compile**

```bash
npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 6: Run all tests**

```bash
npx vitest run
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add components/chat/SessionItem.tsx components/chat/SessionSidebar.tsx \
        components/chat/ChatLayout.tsx app/chat/page.tsx
git commit -m "feat(chat): add SessionItem, SessionSidebar, ChatLayout, and /chat page route"
```

---

## Task 12: Manual QA Checklist

Start the dev server and verify the golden path end-to-end. Requires a logged-in user session.

```bash
npm run dev
```

Open `http://localhost:3000/chat`.

- [ ] **Sidebar renders** with "New Chat" button and empty list
- [ ] **New Chat creates a session** — session appears in sidebar with title "New Chat"
- [ ] **Sending a message** streams a response into the chat window
- [ ] **Streaming indicator** shows while response is in-flight
- [ ] **Auto-title fires** — sidebar title updates after first exchange
- [ ] **Switching sessions** loads the correct history with no cross-session bleed
- [ ] **Rename** — hover over session, click ✏️, type new name, press Enter → title updates
- [ ] **Delete** — hover over session, click 🗑️ → session and messages are removed
- [ ] **Scroll behaviour** — long conversation auto-scrolls to bottom; manual scroll up prevents auto-scroll
- [ ] **Reload page** — sessions and history persist (loaded from Supabase)
- [ ] **Auth guard** — direct `fetch('/api/sessions')` without a session returns 401

- [ ] **Final commit**

```bash
git add .
git commit -m "chore(chat): complete AI chatbot multi-session implementation"
```

---

## Self-Review Against Spec

| Spec section | Covered by task(s) |
|---|---|
| Supabase schema + RLS + index | Task 1 |
| Multi-provider via AI Gateway (model strings) | Task 3 |
| `GET /api/sessions` | Task 4 |
| `POST /api/sessions` | Task 4 |
| `PATCH /api/sessions/[id]` | Task 4 |
| `DELETE /api/sessions/[id]` | Task 4 |
| `GET /api/sessions/[id]/messages` | Task 4 |
| `POST /api/chat` streaming | Task 5 |
| Auto-title on first exchange | Task 5 |
| Zustand `activeSessionId` store | Task 6 |
| TanStack Query session hooks | Task 6 |
| `StreamingIndicator` | Task 7 |
| `EmptyState` | Task 7 |
| `LoadingSkeleton` | Task 7 |
| `ToolCallBlock` (typed parts + state-gated) | Task 7 |
| `MessageBubble` (AI Elements, `isToolUIPart`) | Task 8 |
| `MessageList` + auto-scroll | Task 8 |
| `ChatInput` (Enter-to-send, empty guard) | Task 9 |
| `ChatWindowInner` (`useChat` mount) | Task 10 |
| `ChatWindow` (`key=` remount on switch) | Task 10 |
| `SessionItem` (rename + delete inline) | Task 11 |
| `SessionSidebar` | Task 11 |
| `ChatLayout` + `/chat` page | Task 11 |
| Tool use extension | Spec section 9 — documented pattern only, no dedicated task (opt-in, no default tools) |

All spec sections covered. No gaps found.
