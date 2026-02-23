# Story 003: Email Login Page + Auth API + JWT Session

**Epic**: E-1 (Authentication & Admin)
**Requirements**: FR-01, FR-02, FR-04
**Dependencies**: Story 002
**Priority**: MUST

## Description
Build the login page with email input, the auth API route that validates against the allowlist, and JWT session management with httpOnly cookies.

## Acceptance Criteria
1. `/login` page renders with Immo-Pro logo, email input, and "Sign in" button
2. Invalid email format shows inline validation error
3. `POST /api/auth/login` checks email (case-insensitive) against `allowed_emails` table
4. Approved email → JWT created with {email, name, role, exp}, set as httpOnly Secure SameSite=Strict cookie
5. Non-approved email → JSON response `{success: false, message: "Access denied..."}`
6. After successful login, redirect to `/` (workspace)
7. JWT expires after 24 hours
8. "Sign out" button in header → `POST /api/auth/logout` → clears cookie → redirect to `/login`
9. `GET /api/auth/check` returns current session info or `{authenticated: false}`

## Technical Notes
- Use `jose` library for JWT sign/verify (Edge-compatible, works in Vercel middleware)
- JWT_SECRET from env var
- Login form: React `useActionState` or client-side fetch
- Cookie: `session` name, httpOnly, Secure (in production), SameSite=Strict, Path=/
- Supabase query: `SELECT * FROM allowed_emails WHERE lower(email) = lower($1)`

## Files to Create/Modify
- `app/login/page.tsx` (login page)
- `app/api/auth/login/route.ts` (POST)
- `app/api/auth/logout/route.ts` (POST)
- `app/api/auth/check/route.ts` (GET)
- `lib/auth.ts` (JWT helpers: signToken, verifyToken)
- `app/layout.tsx` (add sign-out button to header)

## Testing
- Visit `/login` — see login form
- Enter non-existent email — see "Access denied" error
- Enter admin email — redirected to `/`
- Check browser cookies — `session` cookie exists (httpOnly)
- Click "Sign out" — redirected to `/login`, cookie cleared
