# Tech Stack — Immo-Pro Report Automation Tool v2

**Document**: Phase 3 — Architecture (Tech Stack)
**Author**: CTO Agent (Architect role)
**Date**: 2026-02-23

---

## Stack Summary

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Frontend** | Next.js 15+ (App Router, TypeScript) | Same stack as LH Portal; best-in-class Vercel integration |
| **Styling** | Tailwind CSS v4 + shadcn/ui | Proven in LH Portal; rapid UI development, consistent design |
| **Backend (Python)** | Vercel Python Serverless Functions | Reuse v1 python-docx code; no separate infrastructure |
| **Database** | Supabase (PostgreSQL) | Free tier sufficient; auth tables, logs, RLS |
| **File Storage** | Supabase Storage | Template files only (uploads are transient) |
| **AI** | Anthropic Claude Sonnet API | Proven in v1 (~$0.05-0.15/report); structured JSON output |
| **Auth** | Custom session (JWT httpOnly cookie) | Lightweight email allowlist; no password management needed |
| **Deployment** | Vercel (single platform) | Frontend + Python functions in one repo, auto-deploy from GitHub |
| **Version Control** | GitHub (private repo) | Existing setup; CI/CD via Vercel integration |

---

## Runtime Versions

| Runtime | Version | Notes |
|---------|---------|-------|
| Node.js | 20+ | Next.js requirement |
| Python | 3.11+ | Vercel Python runtime; supports python-docx + anthropic |
| TypeScript | 5.x (strict mode) | Enforced via tsconfig |
| npm | 10+ | Package management |

---

## Frontend Dependencies

| Package | Purpose |
|---------|---------|
| `next` | React framework (App Router) |
| `react` / `react-dom` | UI library |
| `tailwindcss` | Utility-first CSS |
| `@radix-ui/*` | Headless UI primitives (via shadcn/ui) |
| `lucide-react` | Icon library |
| `zustand` | Lightweight state management (report editing state) |
| `jose` | JWT creation/verification (Edge-compatible) |
| `@supabase/supabase-js` | Supabase client (database, storage) |

---

## Python Dependencies (Serverless Functions)

| Package | Purpose |
|---------|---------|
| `python-docx` | .docx parsing and generation (XML-level access) |
| `lxml` | XML processing (namespace handling, element manipulation) |
| `anthropic` | Claude API client |

**Note**: No web framework needed (FastAPI/Flask). Vercel Python functions are plain Python files with a handler function. File I/O uses `BytesIO` (in-memory, no disk access).

---

## Infrastructure

| Service | Tier | Monthly Cost | Purpose |
|---------|------|-------------|---------|
| Vercel | Hobby (free) | $0 | Next.js hosting + Python functions |
| Supabase | Free | $0 | Database + file storage |
| Anthropic API | Pay-per-use | ~$5-10 | AI analysis (~50 reports/month) |
| GitHub | Free (private) | $0 | Source control + CI/CD trigger |
| **Total** | | **~$5-10/month** | |

**Upgrade path**: If load increases beyond 50 reports/month or response times degrade, upgrade Vercel to Pro ($20/month) for longer timeouts and warm instances.

---

## Decisions Log

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Python backend on Vercel | Vercel Python Serverless | Railway ($5/mo), Fly.io ($4/mo), Render ($7/mo), Node.js rewrite | Simplest: same repo, same platform, no CORS, $0/month. In-memory BytesIO works for file processing. |
| Keep Python (not rewrite to Node) | Keep Python | Full Node.js rewrite using pizzip+xml-parser | python-docx + lxml is battle-tested for XML-level .docx manipulation. Node.js OOXML ecosystem is immature. Rewrite would cost 3-5x dev time with regression risk. |
| zustand over Redux | zustand | Redux, React Context, Jotai | Minimal boilerplate; perfect for single-page editor state. LH Portal used Context but report state is more complex (nested sections/points). |
| Custom JWT auth over Supabase Auth | Custom JWT | Supabase Auth (magic link), NextAuth | Simpler for email-only allowlist. No password reset, no OAuth, no magic links needed. 5-10 internal users. |
| Supabase over raw PostgreSQL | Supabase | Self-hosted Postgres, PlanetScale, Neon | Free tier, familiar from LH Portal, RLS built-in, Storage included. |
