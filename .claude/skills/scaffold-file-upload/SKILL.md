---
name: scaffold-file-upload
description: >-
  Stamps Supabase Storage file upload infrastructure (signed URL API, drag-and-drop
  component, upload hook) into the current Next.js + Supabase project. Invoke when
  a user asks to "add file upload", "scaffold storage", or "add drag and drop upload".
---

# Scaffold: File Upload (Supabase Storage)

Stamps production-ready file upload infrastructure into the current project in one pass.
Architecture: Supabase Storage bucket → signed URL API route → client-side XHR upload → drag-and-drop React component.
Files never pass through the Next.js server — the client PUTs directly to Supabase Storage via a signed URL.

## Before you start

1. Confirm the project uses **Next.js App Router** + **Supabase** (look for `app/` directory and `@supabase/ssr` imports).
2. Ask these customisation questions — state the default for each:

   - **Supabase Storage bucket name?** (default: `uploads`)
   - **Max file size in MB?** (default: `10`)
   - **Allowed file types?** (default: `images and PDFs` — maps to `['image/jpeg', 'image/png', 'image/webp', 'application/pdf']`)
   - **Supabase server client import path?** (default: `@/lib/supabase/server`)

3. Note the answers as `$BUCKET_NAME`, `$MAX_FILE_SIZE_MB`, `$ALLOWED_TYPES`, `$SUPABASE_PATH`.

---

## Step 1 — Supabase Storage bucket setup

### Option A — Supabase Dashboard
1. Go to **Storage** → **New bucket**
2. Name: `$BUCKET_NAME`
3. Public bucket: **enabled** (so public URLs work without signed read URLs)
4. File size limit: `$MAX_FILE_SIZE_MB MB`
5. Allowed MIME types: paste the `$ALLOWED_TYPES` list

### Option B — SQL migration

Create `supabase/migrations/<timestamp>_storage_bucket.sql`:

```sql
-- Create the storage bucket
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  '$BUCKET_NAME',
  '$BUCKET_NAME',
  true,
  $MAX_FILE_SIZE_MB_BYTES,  -- e.g. 10485760 for 10 MB
  array['image/jpeg', 'image/png', 'image/webp', 'application/pdf']
)
on conflict (id) do nothing;

-- RLS: authenticated users can upload to their own folder
create policy "auth users can upload"
  on storage.objects for insert
  to authenticated
  with check (
    bucket_id = '$BUCKET_NAME'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

-- RLS: users can update/delete their own objects
create policy "users own their objects"
  on storage.objects for all
  to authenticated
  using (
    bucket_id = '$BUCKET_NAME'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

-- RLS: public read (bucket is public)
create policy "public read"
  on storage.objects for select
  to public
  using (bucket_id = '$BUCKET_NAME');
```

After creating: `npx supabase db push`

---

## Step 2 — Config

Create `lib/upload/config.ts` from the template at
`templates/project-scaffold/website/lib/upload/config.ts`.

Replace `$BUCKET_NAME` with the chosen bucket name, and adjust `maxFileSizeMb` and `allowedTypes` to match.

---

## Step 3 — Signed URL API route

Create `app/api/upload/signed-url/route.ts` from the template at
`templates/project-scaffold/website/app/api/upload/signed-url/route.ts`.

Replace the `createClient` import path with `$SUPABASE_PATH`.

Key behaviour:
- `POST` receives `{ fileName, contentType, folder? }`
- Validates `contentType` against `UPLOAD_CONFIG.allowedTypes`
- Sanitises the file name (strips path traversal and special chars)
- Builds a unique path: `${folder ?? 'uploads'}/${userId}/${Date.now()}-${sanitisedName}`
- Returns `{ signedUrl, path, token }` — client uploads directly, never via this server
- Returns 401 if unauthenticated, 400 for invalid file type

---

## Step 4 — Upload hook

Create `lib/upload/hooks.ts` from the template at
`templates/project-scaffold/website/lib/upload/hooks.ts`.

Exported API: `useFileUpload()` → `{ upload, isUploading, progress, error, reset }`

`upload(file, folder?)`:
1. Calls `POST /api/upload/signed-url` to get `{ signedUrl, path }`
2. PUTs the file directly to `signedUrl` via `XMLHttpRequest` (for `onprogress`)
3. Sets `Content-Type` header to the file's MIME type
4. Sets `X-Upsert: false` to prevent silent overwrites
5. Returns the final public URL via `UPLOAD_CONFIG.publicUrl(path)` on success

---

## Step 5 — Components

Create from templates at `templates/project-scaffold/website/components/upload/`:

**`FileUpload.tsx`** — drag-and-drop zone:
- Native HTML5 `dragover`/`drop` events (no external DnD library)
- `<input type="file">` click-to-browse fallback
- Renders `<FilePreview>` after file is selected (before and after upload)
- Disabled during upload; shows progress bar
- Props: `onUpload(url, path)`, `accept?`, `folder?`, `className?`

**`FilePreview.tsx`** — file preview:
- Image types: thumbnail via `URL.createObjectURL`
- Non-image types: file icon + name + human-readable size
- `onRemove` prop clears the selection

---

## Step 6 — next.config update

Add `remotePatterns` to `next.config.js` / `next.config.ts` so `next/image` can
render images served from Supabase Storage:

```js
images: {
  remotePatterns: [
    {
      protocol: 'https',
      hostname: '*.supabase.co',
      pathname: '/storage/v1/object/public/**',
    },
  ],
},
```

---

## Step 7 — Post-scaffold TODOs (leave as comments in the code)

| File | TODO |
|---|---|
| `lib/upload/config.ts` | Adjust `allowedTypes` and `maxFileSizeMb` for your use case |
| `components/upload/FileUpload.tsx` | Replace Tailwind classes with project design system |
| `next.config.js` | Add `remotePatterns` entry for Supabase Storage hostname |

---

## Step 8 — Verify

```bash
npx tsc --noEmit   # must pass with 0 errors before handing off
```

Reference implementation: `templates/project-scaffold/website/` in the infiniteleverage-8-agents-template repo.
Setup notes: `templates/project-scaffold/website/docs/upload/setup-notes.md`.
