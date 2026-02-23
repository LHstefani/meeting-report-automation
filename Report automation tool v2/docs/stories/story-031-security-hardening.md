# Story 031: Security Hardening (CSP, CSRF, Input Validation)

**Epic**: E-9 (Polish & Production)
**Requirements**: NFR-02, NFR-06
**Dependencies**: All E-0 through E-7 stories
**Priority**: MUST

## Description
Harden the application security: add Content Security Policy headers, CSRF protection, input validation on all endpoints, and verify data privacy compliance.

## Acceptance Criteria
1. Content Security Policy (CSP) headers set via `next.config.js` or middleware
2. CSP allows only required sources (self, Supabase domain, no inline scripts unless hashed)
3. All API routes validate input: reject unexpected fields, enforce required fields, validate types
4. File upload validation: check MIME type AND file extension (not just extension)
5. File size limit enforced server-side: 5MB for .docx, 2MB for .txt
6. API keys (Anthropic) only accessible in server-side code (never in client bundle)
7. Supabase service role key only used server-side (never exposed to client)
8. All cookies use: httpOnly, secure, sameSite=strict, path=/
9. Rate limiting on login endpoint: max 10 attempts per IP per minute
10. Input sanitization: strip HTML tags from all text inputs before processing
11. No file contents logged or stored permanently (transient processing only)
12. Environment variables documented in `.env.example` (without actual values)
13. Verify: no API keys or secrets in client-side JavaScript bundle (check build output)

## Technical Notes
- CSP: configure in `next.config.js` headers section or in middleware
- Input validation: use `zod` schemas for all API route request bodies
- MIME type check: read file header bytes to verify .docx (PK zip signature) and .txt
- Rate limiting: simple in-memory counter per IP (sufficient for 5-10 users, no Redis needed)
- Sanitization: basic regex strip of HTML tags, or use a small library like `sanitize-html`
- `.env.example`: list all required env vars with placeholder values and descriptions
- Build verification: run `next build` and search output for any env var values

## Files to Create/Modify
- `next.config.js` (add security headers)
- `middleware.ts` (add rate limiting logic for /api/auth/login)
- `lib/validation.ts` (new: zod schemas for all API inputs)
- All `app/api/*/route.ts` files (add input validation with zod)
- All `api/*.py` files (add input validation)
- `.env.example` (new: documented environment variable template)

## Testing
- Check response headers include CSP
- Submit malformed JSON to API → 400 error with validation message
- Upload a .pdf renamed to .docx → rejected (MIME type check)
- Upload 10MB file → rejected with size limit error
- Check client JS bundle for API key strings → none found
- 11 rapid login attempts from same IP → rate limited (429 response)
- Verify cookies have httpOnly, secure, sameSite flags
