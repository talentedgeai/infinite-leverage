---
name: scaffold-auth
description: >-
  Stamps Supabase authentication (email+password + OAuth, server actions, TanStack Form)
  into the current Next.js App Router project. Invoke when a user asks to "add auth",
  "add login", "scaffold authentication", "add Supabase auth", or similar.
---

# Scaffold: Supabase Authentication

Stamps production-ready auth (login, signup, OAuth, session guards) into the current project.
Stack: Supabase Auth + @supabase/ssr + Next.js Server Actions + TanStack Form.

## Before you start

1. Confirm the project uses **Next.js App Router** + **Supabase**.
2. Ask these customisation questions:
   - **Post-login redirect path?** (default: `/dashboard`)
   - **OAuth providers needed?** (e.g. Google, GitHub — default: none, email only)
   - **Site URL env var name?** (default: `NEXT_PUBLIC_SITE_URL`)

3. Note answers as `$POST_LOGIN_PATH`, `$OAUTH_PROVIDERS`, `$SITE_URL_VAR`.

---

## Step 1 — Install dependencies

```bash
npm install @supabase/ssr @supabase/supabase-js @tanstack/react-form
```

Add to `.env.local`:
```
NEXT_PUBLIC_SUPABASE_URL=<from Supabase project settings>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<from Supabase project settings>
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

---

## Step 2 — Supabase clients

### `lib/supabase/server.ts` (SSR-aware, used in Server Components + Actions)
```ts
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() { return cookieStore.getAll() },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options))
          } catch { /* read-only in Server Components — expected */ }
        },
      },
    }
  )
}
```

### `lib/supabase/client.ts` (browser only)
```ts
import { createBrowserClient } from '@supabase/ssr'
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

---

## Step 3 — Session guard

`lib/auth/guards.ts`:
```ts
import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'

// Use in protected Server Components/layouts — NEVER use getSession() server-side
export async function requireAuth(redirectTo = '/login') {
  const supabase = await createClient()
  const { data: { user }, error } = await supabase.auth.getUser()
  if (error || !user) redirect(redirectTo)
  return user
}

export async function getOptionalUser() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  return user
}
```

---

## Step 4 — Server actions

`lib/auth/actions.ts` — `'use server'` file with `loginWithEmail`, `signupWithEmail`, `logout`, `resetPassword`.

Key pattern: server actions return `{ error: string }` on failure, `redirect()` on success.
See full implementation in `templates/project-scaffold/website/lib/auth/actions.ts`.

---

## Step 5 — OAuth callback route

`app/auth/callback/route.ts` — exchanges OAuth/magic-link code for session:
```ts
export async function GET(request: Request) {
  const url = new URL(request.url)
  const code = url.searchParams.get('code')
  const next = url.searchParams.get('next') ?? '$POST_LOGIN_PATH'
  if (code) {
    const supabase = await createClient()
    await supabase.auth.exchangeCodeForSession(code)
  }
  return NextResponse.redirect(`${url.origin}${next}`)
}
```

In Supabase dashboard → Auth → URL Configuration, add:
`http://localhost:3000/auth/callback` (and your production URL).

---

## Step 6 — Pages + forms

- `app/(auth)/login/page.tsx` — Server Component, redirects to `$POST_LOGIN_PATH` if already authenticated
- `app/(auth)/signup/page.tsx` — Server Component, same redirect
- `components/auth/LoginForm.tsx` — TanStack Form, calls `loginWithEmail` server action
- `components/auth/SignupForm.tsx` — TanStack Form, calls `signupWithEmail` server action
- `components/auth/LogoutButton.tsx` — calls `logout` server action

See full implementations in `templates/project-scaffold/website/components/auth/`.

---

## Step 7 — Protect a page

```tsx
// app/dashboard/page.tsx
import { requireAuth } from '@/lib/auth/guards'
export default async function DashboardPage() {
  const user = await requireAuth()
  return <div>Welcome {user.email}</div>
}
```

---

## Post-scaffold TODOs

| File | TODO |
|---|---|
| `lib/auth/actions.ts` | Update `redirect('/dashboard')` to `$POST_LOGIN_PATH` |
| `app/auth/callback/route.ts` | Update redirect to `$POST_LOGIN_PATH` |
| `components/auth/LoginForm.tsx` | Replace Tailwind with project design system |
| `components/auth/SignupForm.tsx` | Replace Tailwind with project design system |
| `app/(auth)/login/page.tsx` | Add branding / logo above form |
| Supabase dashboard | Enable desired OAuth providers + add callback URL |

---

## Critical rules (do not deviate)

- **Always `getUser()` server-side** — `getSession()` does not revalidate with Supabase and is unsafe
- **Server actions for mutations** — no API routes needed for auth
- **`@supabase/ssr` only** — never use `@supabase/supabase-js` `createClient` directly in Next.js
- **Both env vars are public** — `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` are safe to expose; never use service role key client-side

Reference implementation: `templates/project-scaffold/website/` in the infiniteleverage-8-agents-template repo.
