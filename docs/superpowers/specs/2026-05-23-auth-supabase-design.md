# Auth — Supabase + Next.js App Router

> Reference spec for scaffolding Supabase authentication into any Next.js App Router project.
> Status: Approved

## Architecture

Five-layer pattern:
1. **Supabase clients** — SSR-aware server client + browser client
2. **Server actions** — login, signup, logout, password reset (no API routes needed)
3. **Auth callback route** — handles OAuth + magic link redirects
4. **Server Component guard** — `requireAuth()` helper for protected pages
5. **UI** — LoginForm + SignupForm using TanStack Form

## Supabase client setup

### Server client (`lib/supabase/server.ts`)
Uses `@supabase/ssr` `createServerClient` with Next.js `cookies()`. Called in Server Components, Route Handlers, and Server Actions.

### Browser client (`lib/supabase/client.ts`)
Uses `@supabase/ssr` `createBrowserClient`. Called in Client Components only.

## Auth flow

### Email + password
1. User submits LoginForm → server action `loginWithEmail`
2. Action calls `supabase.auth.signInWithPassword`
3. On success: `redirect('/dashboard')` (customisable)
4. On error: return `{ error: message }` to form

### OAuth (Google, GitHub, etc.)
1. User clicks OAuth button → server action `loginWithOAuth`
2. Action calls `supabase.auth.signInWithOAuth({ provider, redirectTo: /auth/callback })`
3. Browser redirected to provider
4. Provider redirects to `/auth/callback?code=...`
5. Callback route exchanges code for session → redirect to app

### Signup
1. User submits SignupForm → server action `signupWithEmail`
2. Action calls `supabase.auth.signUp`
3. On success: redirect to email confirmation page
4. Email confirmation link hits `/auth/callback`

### Session guard
Server Components call `requireAuth()` which:
- Gets user via `supabase.auth.getUser()` (not `getSession()` — getSession is not safe server-side)
- Redirects to `/login` if no user
- Returns `user` object

## Key decisions

- **Never use `getSession()` server-side** — it reads from cookie without revalidating with Supabase. Always use `getUser()`.
- **No middleware for auth** — use Server Component `requireAuth()` per page. Middleware adds latency on every request; per-page guards are explicit.
- **Server actions over API routes** — auth mutations are server actions, no extra API layer needed.
- **TanStack Form** — forms use `useForm` with `zod` validation. Error state surfaced via `form.state.errors` not local useState.

## File map

| File | Responsibility |
|---|---|
| `lib/supabase/server.ts` | SSR-aware server Supabase client |
| `lib/supabase/client.ts` | Browser Supabase client |
| `lib/auth/actions.ts` | Server actions: login, signup, logout, resetPassword |
| `lib/auth/guards.ts` | `requireAuth()` helper for Server Components |
| `app/auth/callback/route.ts` | OAuth + magic link code exchange |
| `app/(auth)/login/page.tsx` | Login page (Server Component) |
| `app/(auth)/signup/page.tsx` | Signup page (Server Component) |
| `components/auth/LoginForm.tsx` | TanStack Form login form (Client Component) |
| `components/auth/SignupForm.tsx` | TanStack Form signup form (Client Component) |
| `components/auth/LogoutButton.tsx` | Logout trigger (Client Component) |

## Environment variables

```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

Both are public — never use service role key client-side.
