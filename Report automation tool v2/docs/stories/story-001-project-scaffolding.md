# Story 001: Project Scaffolding + GitHub Repo + Vercel Link

**Epic**: E-0 (Project Setup)
**Requirements**: NFR-07
**Dependencies**: None (first story)
**Priority**: MUST

## Description
Create the Next.js project with TypeScript, Tailwind CSS, and shadcn/ui. Initialize the GitHub repository, link to Vercel for auto-deploy. Set up the monorepo structure with a root `api/` directory for Python serverless functions and the `src/` directory for shared Python modules.

## Acceptance Criteria
1. Next.js 15+ project created with App Router and TypeScript strict mode
2. Tailwind CSS v4 configured and working
3. shadcn/ui initialized with at least `button`, `input`, `card` components
4. GitHub private repo created (`report-automation-v2` or similar)
5. Vercel project linked to GitHub repo with auto-deploy on push
6. Root `api/` directory exists for Python serverless functions
7. `src/` directory contains the v1 Python modules (copied from current location)
8. `requirements.txt` at root lists Python dependencies (python-docx, anthropic, lxml)
9. `vercel.json` configured for Python runtime
10. `.env.example` lists all required environment variables
11. Basic root layout renders with Immo-Pro logo and app title
12. Dev server starts without errors (`npm run dev`)

## Technical Notes
- Use `npx create-next-app@latest` with TypeScript, App Router, Tailwind
- shadcn/ui: `npx shadcn@latest init` then add components
- Python modules: copy from `Report automation tool v2/src/` into project `src/`
- `vercel.json`: configure `functions` with `runtime: "python3.11"` and `maxDuration: 90`
- Logo file: copy from `Report automation tool v2/LOGO/`

## Files to Create
- `app/layout.tsx` (root layout)
- `app/page.tsx` (temporary landing page)
- `api/` (empty, placeholder)
- `src/` (Python modules)
- `requirements.txt`
- `vercel.json`
- `.env.example`
- `public/logo.png`

## Testing
- `npm run dev` starts without errors
- Visit `http://localhost:3000` — see logo + title
- `git push` triggers Vercel deploy
- Vercel deploy succeeds (green)
