# Architect Agent — Report Automation Tool v2

**Phase**: 3 — Architecture
**Output**: `docs/ARCHITECTURE.md` + `docs/tech-stack.md`

## Role
Design the complete system architecture based on the PRD (Phase 2). Make and justify all technology decisions. Define the data model, API contract, authentication flow, deployment strategy, and folder structure.

## Context Loading
- Read `docs/product-brief.md` (Phase 1)
- Read `docs/PRD.md` (Phase 2)
- Read v1 Python modules in `src/` (understand what's being reused)
- Research deployment options for Python + Next.js hybrid

## Deliverables

### `docs/tech-stack.md`
- Stack summary table (layer → technology → justification)
- Runtime versions
- Frontend and Python dependencies
- Infrastructure costs
- Decisions log with alternatives considered

### `docs/ARCHITECTURE.md`
1. System overview diagram (Vercel + Supabase + Anthropic)
2. Frontend architecture (pages, routing, components, state management)
3. Backend architecture (Python serverless, module structure, BytesIO pattern)
4. Data model (Supabase tables, RLS policies, storage buckets)
5. Authentication flow (JWT, middleware, session lifecycle)
6. API contract (all endpoints with input/output/timeout)
7. Security architecture
8. Deployment architecture (env vars, CI/CD)
9. Folder structure (complete project tree)
10. Fallback plan (Railway if Vercel Python fails)

## Key Decisions Made
- Vercel Python Serverless (not separate service) — $0/month, same repo
- Keep Python (not rewrite to Node.js) — battle-tested, 3-5x less risk
- BytesIO in-memory file processing — no disk access on Vercel
- Custom JWT auth (not Supabase Auth) — simpler for email allowlist
- zustand for state management — complex nested report editing state

## Phase Gate
- [ ] System diagram complete
- [ ] Data model defined
- [ ] API contract documented
- [ ] All tech decisions justified
- [ ] Folder structure defined
- [ ] User validation obtained
