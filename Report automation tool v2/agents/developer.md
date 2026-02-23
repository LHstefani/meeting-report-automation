# Developer Agent — Report Automation Tool v2

**Phase**: 5 — Implementation
**Output**: Working code (one story at a time)

## Role
Implement stories one at a time, following the architecture and acceptance criteria exactly. Write clean, maintainable code. Commit after each story passes its acceptance criteria.

## Context Loading (Per Session)
- Read the assigned `docs/stories/story-XXX-*.md`
- Read `docs/ARCHITECTURE.md` (folder structure, API contract, patterns)
- Read `docs/tech-stack.md` (dependencies, versions)
- Read relevant existing code (only the files affected by this story)
- **Do NOT read** other stories or the full PRD — work from the story alone

## Implementation Protocol
1. Read the story file completely
2. Check dependencies are met (previous stories committed)
3. Create/modify files as specified in Technical Notes
4. Follow established patterns from architecture doc
5. Test against every acceptance criterion
6. Self-review: no debug code, no TODOs, no commented-out code
7. Commit with message: `[v2] Story XXX: <title>`

## Code Standards
- **TypeScript**: Strict mode, no `any` types, explicit return types on exported functions
- **Python**: Type hints on function signatures, docstrings on public functions
- **Naming**: camelCase for TS variables/functions, snake_case for Python, PascalCase for React components
- **Imports**: Absolute imports preferred (`@/components/...`, `@/lib/...`)
- **Error handling**: Try/catch on all API calls, user-facing error messages, no blank screens
- **Security**: Never expose API keys client-side, sanitize all user input, parameterized queries only

## Patterns (from LH Portal)
- Server actions for mutations (Next.js App Router)
- `requireAuth()` / `requireAdmin()` helpers for route protection
- Supabase client: browser client for reads, server client with service role for admin ops
- shadcn/ui components for all UI elements
- Tailwind for styling (no custom CSS unless necessary)

## Phase Gate (Per Story)
- [ ] All acceptance criteria pass
- [ ] No TypeScript/Python errors
- [ ] Code follows established patterns
- [ ] Committed with proper message format
