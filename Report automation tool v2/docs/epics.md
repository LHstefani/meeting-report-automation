# Epics — Immo-Pro Report Automation Tool v2

**Document**: Phase 4 — Stories (Epic Overview)
**Author**: CTO Agent (Scrum Master role)
**Date**: 2026-02-23
**Source**: `docs/PRD.md` (Phase 2) + `docs/ARCHITECTURE.md` (Phase 3)

---

## Epic Summary

| Epic | Name | Stories | Requirements | Priority |
|------|------|---------|-------------|----------|
| E-0 | Project Setup | 001-002 | NFR-07 | Foundation |
| E-1 | Authentication & Admin | 003-005 | FR-01 to FR-04 | MUST |
| E-2 | Python Backend & File Upload | 006-010 | FR-05 to FR-09 | MUST |
| E-3 | AI Analysis | 011-013 | FR-10 to FR-13 | MUST |
| E-4 | Document Preview & Editing | 014-021 | FR-14 to FR-21 | MUST |
| E-5 | Quality Analysis | 022-023 | FR-22 to FR-25 | MUST |
| E-6 | Feedback & Re-Generation | 024-025 | FR-26, FR-27 | MUST |
| E-7 | Report Generation & Download | 026-027 | FR-28 to FR-30 | MUST |
| E-8 | Templates & Usage Tracking | 028-029 | FR-31 to FR-34 | SHOULD/COULD |
| E-9 | Polish & Production | 030-032 | NFR-01 to NFR-08 | MUST |

**Total**: 32 stories across 10 epics

---

## Dependency Chain

```
E-0 (Setup)
 └─> E-1 (Auth)
      └─> E-2 (Upload & Parsing)
           └─> E-3 (AI Analysis)
                └─> E-4 (Preview & Editing)
                     ├─> E-5 (Quality)
                     ├─> E-6 (Feedback)
                     └─> E-7 (Download)
                          └─> E-8 (Templates & Tracking)
                               └─> E-9 (Polish & Deploy)
```

E-5, E-6 can be done in parallel after E-4. E-7 depends on E-5 (quality gate).

---

## E-0: Project Setup (Stories 001-002)

**Goal**: Scaffold the Next.js project, create the GitHub repo, set up Supabase, and establish the monorepo structure with Python functions.

| Story | Title | Requirements |
|-------|-------|-------------|
| 001 | Project scaffolding + GitHub repo + Vercel link | NFR-07 |
| 002 | Supabase schema + RLS + storage + seed data | NFR-02 |

---

## E-1: Authentication & Admin (Stories 003-005)

**Goal**: Email-based authentication with allowlist, session management, and admin email management.

| Story | Title | Requirements |
|-------|-------|-------------|
| 003 | Email login page + auth API + JWT session | FR-01, FR-02, FR-04 |
| 004 | Route protection middleware + session check | FR-04, NFR-02 |
| 005 | Admin email allowlist management | FR-03 |

---

## E-2: Python Backend & File Upload (Stories 006-010)

**Goal**: Set up the Python serverless functions on Vercel, adapt v1 modules for BytesIO, and build the file upload UI with parsing.

| Story | Title | Requirements |
|-------|-------|-------------|
| 006 | Python backend setup (Vercel config, BytesIO adaptation) | NFR-07 |
| 007 | Report upload + parse-report endpoint | FR-05, FR-07 |
| 008 | Transcript upload + parse-transcript endpoint | FR-05, FR-08 |
| 009 | First report mode (template selector) | FR-06 |
| 010 | Parsing summary + proceed to analysis | FR-09 |

---

## E-3: AI Analysis (Stories 011-013)

**Goal**: Send parsed data to Claude API, handle both update and first-report modes, display results.

| Story | Title | Requirements |
|-------|-------|-------------|
| 011 | AI analysis endpoint + loading UX | FR-10, FR-11 |
| 012 | First report analysis mode | FR-12 |
| 013 | Token usage + cost display | FR-13 |

---

## E-4: Document Preview & Editing (Stories 014-021)

**Goal**: Build the document-like preview with inline editing — the core UI innovation of v2.

| Story | Title | Requirements |
|-------|-------|-------------|
| 014 | zustand store + document preview shell | FR-14 |
| 015 | Point rows (number, title, content, for_whom, due) | FR-14 |
| 016 | Content differentiation (existing grey vs proposed bold) | FR-15 |
| 017 | Inline editing (click-to-edit all fields) | FR-16 |
| 018 | Metadata panel (editable, fixed position) | FR-17 |
| 019 | Info exchange table (editable, add/delete rows) | FR-18 |
| 020 | Planning table (editable, add/delete items) | FR-19 |
| 021 | Add/remove points + accept/reject toggles | FR-20, FR-21 |

---

## E-5: Quality Analysis (Stories 022-023)

**Goal**: Automated quality checks with blocking and warning criteria.

| Story | Title | Requirements |
|-------|-------|-------------|
| 022 | Quality check endpoint (Q1-Q10 logic) | FR-22, FR-23, FR-24 |
| 023 | Quality panel UI + score display | FR-22, FR-24, FR-25 |

---

## E-6: Feedback & Re-Generation (Stories 024-025)

**Goal**: User can provide natural-language feedback and trigger AI re-analysis.

| Story | Title | Requirements |
|-------|-------|-------------|
| 024 | Feedback input + analyze-feedback endpoint | FR-26, FR-27 |
| 025 | Re-generation flow + updated proposal display | FR-27 |

---

## E-7: Report Generation & Download (Stories 026-027)

**Goal**: Generate the final .docx and enable download with quality gate.

| Story | Title | Requirements |
|-------|-------|-------------|
| 026 | Generate-report endpoint (BytesIO, bold management) | FR-28, FR-29 |
| 027 | Download UI + filename + quality gate + reset | FR-29, FR-30 |

---

## E-8: Templates & Usage Tracking (Stories 028-029)

**Goal**: Admin template management and generation logging with usage dashboard.

| Story | Title | Requirements |
|-------|-------|-------------|
| 028 | Template management (admin upload, PM selection) | FR-31, FR-32 |
| 029 | Usage logging + admin usage dashboard | FR-33, FR-34 |

---

## E-9: Polish & Production (Stories 030-032)

**Goal**: Error handling, security hardening, and production deployment.

| Story | Title | Requirements |
|-------|-------|-------------|
| 030 | Error handling + loading states + edge cases | NFR-01, NFR-03 |
| 031 | Security hardening (CSP, CSRF, input validation) | NFR-02, NFR-06 |
| 032 | Production deployment + final testing | NFR-04, NFR-05 |
