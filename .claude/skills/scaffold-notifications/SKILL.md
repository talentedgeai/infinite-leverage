---
name: scaffold-notifications
description: >-
  Stamps in-app notification infrastructure (Supabase table, realtime subscription,
  bell UI) into the current Next.js + Supabase project. Invoke when a user asks to
  "add notifications", "scaffold notification bell", or "add realtime notifications".
---

# Scaffold: In-App Notifications

Stamps production-ready in-app notifications into the current project in one pass.
Architecture: Supabase persistence + Realtime → Next.js API routes → TanStack Query → React UI.

## Before you start

1. Confirm the project uses **Next.js App Router** + **Supabase** (look for `app/` directory and `@supabase/ssr` imports).
2. Ask these customisation questions — state the default for each:

   - **Supabase server client import path?** (default: `@/lib/supabase/server`)
   - **Supabase browser client import path?** (default: `@/lib/supabase/client`)
   - **Notification bell placement?** (default: `header` — tells developer where to mount `<NotificationBell />`)

3. Note the answers as `$SUPABASE_SERVER_PATH`, `$SUPABASE_CLIENT_PATH`, `$BELL_PLACEMENT`.

---

## Step 1 — Database migration

Create `supabase/migrations/<timestamp>_notifications_table.sql`:

```sql
create table notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users not null,
  type text not null,          -- 'info' | 'success' | 'warning' | 'error'
  title text not null,
  body text,
  read_at timestamptz,         -- null = unread
  action_url text,             -- optional deep link
  created_at timestamptz default now()
);
alter table notifications enable row level security;
create policy "user owns notifications"
  on notifications for all using (auth.uid() = user_id);
create index on notifications(user_id, read_at, created_at desc);
```

After creating: `npx supabase db push`

---

## Step 2 — Install dependencies

```bash
npm install @tanstack/react-query date-fns
```

If TanStack Query is already installed, skip. Confirm with `grep @tanstack/react-query package.json`.

---

## Step 3 — API routes

### `app/api/notifications/route.ts` — list unread + recent

- `GET` — returns unread + recent 20, ordered by `created_at DESC`; 401 if not authenticated
- Explicit `.eq('user_id', user.id)` ownership check before RLS

### `app/api/notifications/[id]/read/route.ts` — mark single as read

- `POST` — sets `read_at = now()` with ownership check; 401 if not authenticated

See full implementations in `templates/project-scaffold/website/app/api/notifications/`.

---

## Step 4 — TanStack Query hooks

Create `lib/notifications/queries.ts` exporting:

- `useNotifications()` — fetches notifications array, `queryKey: ['notifications']`
- `useMarkAsRead()` — mutation (TanStack v5 object syntax), optimistically updates `read_at`, invalidates on settle
- `useUnreadCount()` — derived from `useNotifications()` data (filter where `read_at === null`)

See full implementation in `templates/project-scaffold/website/lib/notifications/queries.ts`.

---

## Step 5 — Components

Create all components under `components/notifications/`:

**`NotificationBell.tsx`**
- Lucide `Bell` icon (comment `// TODO: replace with project design system icon`)
- Badge showing unread count from `useUnreadCount()`
- Opens a popover/dropdown containing `<NotificationList />`
- Supabase Realtime subscription via `supabase.channel()` with `postgres_changes` on INSERT filtered by `user_id = user.id`
- On INSERT → `queryClient.invalidateQueries({ queryKey: ['notifications'] })`
- Cleanup on unmount: `supabase.removeChannel(channel)`

**`NotificationList.tsx`**
- Maps notifications array → `<NotificationItem />`
- Empty state when array is empty
- "Mark all read" button (calls `useMarkAsRead` for each unread)

**`NotificationItem.tsx`**
- Shows `title`, truncated `body`, relative time via `formatDistanceToNow` from `date-fns`
- Comment `// TODO: npm install date-fns` if not already installed
- Optional `action_url` rendered as a link
- Comment `// TODO: replace Tailwind classes with project design system`

See full implementations in `templates/project-scaffold/website/components/notifications/`.

---

## Step 6 — Mount the bell

Add `<NotificationBell />` to the project's header/nav component at `$BELL_PLACEMENT`.

```tsx
import { NotificationBell } from '@/components/notifications/NotificationBell'
// Place inside your header JSX:
// <NotificationBell />
```

---

## Step 7 — Post-scaffold TODOs

| File | TODO |
|---|---|
| `components/notifications/NotificationBell.tsx` | Replace bell icon with project design system icon |
| `components/notifications/NotificationItem.tsx` | Replace Tailwind classes with project design system |
| `app/api/notifications/route.ts` | Add push notification integration (Expo, web push) if needed |

---

## Step 8 — Verify

```bash
npx tsc --noEmit   # must pass with 0 errors before handing off
```

Reference implementation: `templates/project-scaffold/website/` in the infiniteleverage-8-agents-template repo.
