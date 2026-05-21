# web-publisher — Project Persona

Project-specific rules for the web-publisher agent. These override or extend global defaults.

## How this file is populated

Fill in the stack details below once the developer scaffolds the website.
The web-publisher reads this file on first invocation to understand the project's publishing pipeline.

## Project-specific rules
<!-- What the publisher must always do for this project -->
- (e.g. Always update the blog index after publishing a new post)
- (e.g. Always run image optimization before committing)

<!-- What the publisher must never do for this project -->
- (e.g. Never push directly to main — always stage and hand off to operator)
- (e.g. Never publish a post without a hero image)

## Publishing pipeline
<!-- How content moves from source to website for this project -->
- Source: `content/topics/<slug>/blog.md`
- Output: (e.g. `website/pages/blog/<slug>.jsx`)
- Blog index: (e.g. `website/pages/blog/index.jsx`)
- Image optimization: (e.g. Sharp via next/image, output to `website/public/images/`)

## Stack and tools
- Framework: (e.g. Next.js App Router)
- Styling: (e.g. Tailwind CSS + shadcn/ui)
- Deployment: (e.g. Vercel — auto-deploy on push to main)
