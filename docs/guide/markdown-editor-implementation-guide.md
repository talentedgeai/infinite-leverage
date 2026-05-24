# Markdown Editor Implementation Guide

A production-grade guide for implementing a WYSIWYG markdown editor using `@mdxeditor/editor` v3.52+. Based on `src/components/custom/MarkdownEditor.tsx`.

---

## 1. Dependency

```bash
pnpm add @mdxeditor/editor
```

The library is built on Lexical (Meta) and provides a rich-text editing surface that serializes to/from markdown.

---

## 2. Architecture

A **controlled React component** using `forwardRef` + `useImperativeHandle`, exposing `getMarkdown()` for imperative reads. Two modes:

- **Edit mode** — MDXEditor surface with toolbar
- **Preview mode** — rendered markdown via `react-markdown` (read-only)

---

## 3. Imports

```tsx
'use client';

import React, {
  useRef, useState, forwardRef, useImperativeHandle,
  useCallback, createContext, useContext,
} from 'react';
import '@mdxeditor/editor/style.css';
import {
  MDXEditor,
  type MDXEditorMethods,
  headingsPlugin,
  listsPlugin,
  quotePlugin,
  markdownShortcutPlugin,
  linkPlugin,
  linkDialogPlugin,
  toolbarPlugin,
  UndoRedo,
  BoldItalicUnderlineToggles,
  BlockTypeSelect,
  ListsToggle,
  Separator,
  thematicBreakPlugin,
  CreateLink,
  codeBlockPlugin,
  codeMirrorPlugin,
  CodeMirrorEditor,
  tablePlugin,
  imagePlugin,
  frontmatterPlugin,
  searchPlugin,
  InsertTable,
  InsertImage,
  InsertFrontmatter,
  InsertCodeBlock,
  InsertThematicBreak,
  ButtonWithTooltip,
  directivesPlugin,
  type DirectiveEditorProps,
} from '@mdxeditor/editor';
```

---

## 4. Props & Handle Interfaces

```tsx
export interface MarkdownEditorProps {
  value: string;
  onChange: (value: string) => void;
  showPreviewToggle?: boolean;      // default: true
  minHeight?: string;               // default: "280px"
  placeholder?: React.ReactNode;
  className?: string;
  contentEditableClassName?: string;
  autoFocus?: boolean;              // default: true
}

export interface MarkdownEditorHandle {
  getMarkdown: () => string;
}
```

---

## 5. Component Shell

```tsx
export const MarkdownEditor = forwardRef<
  MarkdownEditorHandle | null,
  MarkdownEditorProps
>(function MarkdownEditor(
  { value, onChange, showPreviewToggle = true, minHeight = '280px',
    placeholder, className = '', contentEditableClassName, autoFocus = true },
  ref
) {
  const [mode, setMode] = useState<'edit' | 'preview'>('edit');
  const editorRef = useRef<MDXEditorMethods>(null);

  useImperativeHandle(ref, () => ({
    getMarkdown: () => editorRef.current?.getMarkdown() ?? '',
  }), []);

  // ... handlers and JSX
});
```

---

## 6. Plugin Configuration — The Complete Stack

### 6.1 Structural Plugins

```tsx
headingsPlugin(),         // H1-H6, keyboard shortcuts (##, ###)
listsPlugin(),            // ordered + unordered lists
quotePlugin(),            // blockquotes
thematicBreakPlugin(),    // horizontal rules (---)
```

### 6.2 Code Block Plugins

```tsx
codeBlockPlugin({
  defaultCodeBlockLanguage: 'text',
  codeBlockEditorDescriptors: [
    codeBlockWithTitleDescriptor,    // custom: title bar from meta
    plainTextCodeBlockDescriptor,    // custom: plain text blocks
  ],
}),
codeMirrorPlugin({
  codeBlockLanguages: {
    text: 'Plain text',    js: 'JavaScript',    jsx: 'JSX',
    ts: 'TypeScript',      tsx: 'TypeScript (React)',
    css: 'CSS',            json: 'JSON',
    md: 'Markdown',        html: 'HTML',
    bash: 'Bash',          shell: 'Shell',       sh: 'Shell',
    sql: 'SQL',            python: 'Python',     py: 'Python',
    yaml: 'YAML',          yml: 'YAML',
  },
}),
```

`codeBlockEditorDescriptors` customize code block rendering. The `codeBlockWithTitleDescriptor` (priority 0) wraps blocks with a title extracted from fenced code meta (e.g., ` ```js title="Example" `). The `plainTextCodeBlockDescriptor` (priority -10) handles blocks with no language.

### 6.3 Link, Table, Image, Frontmatter, Search

```tsx
linkPlugin(),             // renders links
linkDialogPlugin(),       // dialog for inserting/editing links
tablePlugin(),            // full table editing
imagePlugin(),            // image insertion via URL dialog
frontmatterPlugin(),      // YAML frontmatter block
searchPlugin(),           // Ctrl/Cmd+F search
```

### 6.4 Markdown Shortcut Plugin

```tsx
markdownShortcutPlugin(),
```

Enables typing raw markdown syntax (`**bold**`, `*italic*`, `` `code` ``) and having it auto-converted to formatted text.

### 6.5 Directives Plugin (Custom Extensions)

```tsx
directivesPlugin({
  directiveDescriptors: [attachmentsDirectiveDescriptor],
}),
```

Enables custom block-level directives. The `::attachments` directive renders as a styled placeholder.

### 6.6 Toolbar Plugin

```tsx
toolbarPlugin({
  toolbarContents: () => (
    <>
      <UndoRedo />
      <Separator />
      <BlockTypeSelect />
      <Separator />
      <BoldItalicUnderlineToggles />
      <Separator />
      <ListsToggle />
      <Separator />
      <CreateLink />
      <Separator />
      <InsertCodeBlock />
      <InsertTable />
      <InsertImage />
      <InsertThematicBreak />
      <Separator />
      <InsertAttachmentsToolbarButton />
      <Separator />
      <ButtonWithTooltip
        title={copyToolbarFeedback ? 'Copied!' : 'Copy markdown'}
        onClick={handleToolbarCopy}
      >
        <Copy className="h-4 w-4" />
      </ButtonWithTooltip>
    </>
  ),
}),
```

---

## 7. Custom Extensions

### 7.1 Code Block with Title

Parses `title="..."` from the code fence meta string and renders it above the CodeMirror editor:

```tsx
function parseCodeBlockTitle(meta: string | null | undefined): string | null {
  if (!meta || !meta.trim()) return null;
  const match = meta.match(/title\s*=\s*["']([^"']*)["']/);
  return match ? match[1].trim() || null : null;
}

function CodeBlockEditorWithTitle(props: React.ComponentProps<typeof CodeMirrorEditor>) {
  const title = parseCodeBlockTitle(props.meta);
  const editor = (props.language == null || props.language === '')
    ? <PlainTextCodeBlockEditor {...props} />
    : <CodeMirrorEditor {...props} />;
  return (
    <div className="flex flex-col gap-1">
      {title && (
        <div className="text-xs font-semibold uppercase tracking-wide text-neutral-600">
          {title}
        </div>
      )}
      <div className="min-h-0">{editor}</div>
    </div>
  );
}

const codeBlockWithTitleDescriptor = {
  priority: 0,
  match: () => true,
  Editor: CodeBlockEditorWithTitle,
} as const;

const plainTextCodeBlockDescriptor = {
  priority: -10,
  match: (language: string | null | undefined) => language == null || language === '',
  Editor: PlainTextCodeBlockEditor,
} as const;
```

### 7.2 Attachments Directive

A custom leaf directive that renders a placeholder for file attachments:

```tsx
function AttachmentsDirectiveEditor(_props: DirectiveEditorProps) {
  return (
    <div className="flex items-center gap-2 rounded-md border border-dashed
                    border-neutral-300 bg-neutral-50 px-3 py-2 text-sm text-neutral-600"
         data-attachments-placeholder>
      <Paperclip className="h-4 w-4 shrink-0 text-neutral-500" />
      <span>Attachments will appear here</span>
    </div>
  );
}

const attachmentsDirectiveDescriptor = {
  testNode: (node: { name?: string }) => node.name === 'attachments',
  name: 'Attachments',
  attributes: [],
  hasChildren: false,
  type: 'leafDirective' as const,
  Editor: AttachmentsDirectiveEditor,
};
```

Toolbar button with guard against duplicates:

```tsx
function hasAttachmentsPlaceholder(md: string): boolean {
  return /::\s*attachments|:::\s*attachments/.test(md);
}

const AttachmentsInsertContext = createContext<{
  insertAttachments: () => void
} | null>(null);

function InsertAttachmentsToolbarButton() {
  const ctx = useContext(AttachmentsInsertContext);
  if (!ctx) return null;
  return (
    <ButtonWithTooltip title="Insert attachments placeholder"
                       onClick={ctx.insertAttachments}>
      <Paperclip className="h-4 w-4" />
    </ButtonWithTooltip>
  );
}

// In the component:
const insertAttachments = useCallback(() => {
  const md = editorRef.current?.getMarkdown() ?? '';
  if (hasAttachmentsPlaceholder(md)) return;
  editorRef.current?.insertMarkdown('\n\n::attachments\n\n');
}, []);
```

---

## 8. Clipboard Handling

Critical for a good editing experience: intercept paste/copy to preserve markdown fidelity, but **skip interception inside CodeMirror code blocks** so native code editing works:

```tsx
function isInsideCodeMirror(target: EventTarget | null): boolean {
  const el = target as HTMLElement | null;
  if (!el) return false;
  return Boolean(el.closest?.('.cm-editor, .cm-content'));
}

const handlePasteCapture = (e: React.ClipboardEvent) => {
  if (isInsideCodeMirror(e.target)) return;
  const raw = e.clipboardData?.getData('text/plain');
  if (!raw || !editorRef.current) return;
  e.preventDefault();
  e.stopPropagation();
  const normalized = raw.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  editorRef.current.insertMarkdown(normalized);
};

const handleCopyCapture = (e: React.ClipboardEvent) => {
  if (isInsideCodeMirror(e.target)) return;
  const markdown = editorRef.current?.getSelectionMarkdown?.();
  if (markdown == null || markdown === '' || !e.clipboardData) return;
  e.preventDefault();
  e.stopPropagation();
  e.clipboardData.setData('text/plain', markdown);
};
```

Attach to the wrapper div:

```tsx
<div onPasteCapture={handlePasteCapture}
     onCopyCapture={handleCopyCapture}>
  <MDXEditor ... />
</div>
```

---

## 9. Edit/Preview Toggle

```tsx
{mode === 'edit' ? (
  <AttachmentsInsertContext.Provider value={{ insertAttachments }}>
    <div className="md-editor flex-1 min-h-0 overflow-visible rounded-sm
                    border border-sidebar-border bg-white"
         style={{ minHeight }}
         onPasteCapture={handlePasteCapture}
         onCopyCapture={handleCopyCapture}>
      <MDXEditor
        ref={editorRef}
        className="min-h-full"
        contentEditableClassName={cn('md-editor-content neutral max-w-none',
                                      contentEditableClassName)}
        markdown={markdownStr}
        onChange={onChange}
        plugins={[ /* all plugins from section 6 */ ]}
      />
    </div>
  </AttachmentsInsertContext.Provider>
) : (
  <div className="flex-1 min-h-0 overflow-auto rounded-sm
                  border border-sidebar-border bg-white px-4 py-3"
       style={{ minHeight }}>
    <div className="max-w-none text-sm leading-relaxed text-gray-700">
      <MarkdownRenderer>{markdownStr || '_No content_'}</MarkdownRenderer>
    </div>
  </div>
)}
```

The preview mode uses a separate `MarkdownRenderer` component (based on `react-markdown` with `remarkGfm`, `remarkBreaks`, `rehypeRaw`) for accurate rendering.

---

## 10. Usage Example

```tsx
import { MarkdownEditor, type MarkdownEditorHandle } from '@/components/custom/MarkdownEditor';

function MyForm() {
  const [content, setContent] = useState('');
  const editorRef = useRef<MarkdownEditorHandle>(null);

  const handleSave = () => {
    const md = editorRef.current?.getMarkdown() ?? '';
    // persist md...
  };

  return (
    <div>
      <MarkdownEditor
        ref={editorRef}
        value={content}
        onChange={setContent}
        minHeight="400px"
        placeholder="Start writing..."
      />
      <button onClick={handleSave}>Save</button>
    </div>
  );
}
```

---

## 11. Plugin Summary Table

| Plugin | Purpose | Required |
|---|---|---|
| `headingsPlugin` | H1-H6 headings | Yes |
| `listsPlugin` | Ordered/unordered lists | Yes |
| `quotePlugin` | Blockquotes | Yes |
| `thematicBreakPlugin` | Horizontal rules | Yes |
| `codeBlockPlugin` | Fenced code blocks with custom descriptors | Yes |
| `codeMirrorPlugin` | Syntax-highlighted code editing | Yes |
| `linkPlugin` | Link rendering | Yes |
| `linkDialogPlugin` | Link insertion dialog | Yes |
| `markdownShortcutPlugin` | Real-time markdown-to-rich-text conversion | Yes |
| `tablePlugin` | Table editing | Recommended |
| `imagePlugin` | Image insertion | Recommended |
| `frontmatterPlugin` | YAML frontmatter | Optional |
| `searchPlugin` | In-editor search | Recommended |
| `directivesPlugin` | Custom block directives | Optional |
| `toolbarPlugin` | Toolbar with buttons | Yes |

---

## 12. Key Design Decisions

1. **Controlled component** — `value`/`onChange` props keep React as the source of truth.
2. **forwardRef + useImperativeHandle** — exposes `getMarkdown()` for form submissions without lifting state unnecessarily.
3. **Clipboard interception with CodeMirror bypass** — paste/copy work correctly both in prose and inside code blocks.
4. **Custom code block descriptors** — title extraction from meta and plain-text fallback provide a polished editing experience.
5. **Context for toolbar extensions** — `AttachmentsInsertContext` allows toolbar buttons to access editor methods without prop drilling.
6. **Preview mode via separate renderer** — avoids the complexity of making MDXEditor itself handle read-only mode; uses battle-tested `react-markdown` instead.
