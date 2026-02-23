# Story 004: Route Protection Middleware + Session Check

**Epic**: E-1 (Authentication & Admin)
**Requirements**: FR-04, NFR-02
**Dependencies**: Story 003
**Priority**: MUST

## Description
Add Next.js middleware that verifies the JWT session on every request to protected routes. Unauthenticated users are redirected to `/login`. Admin routes additionally check for admin role.

## Acceptance Criteria
1. `middleware.ts` intercepts all requests to `/(workspace)` and `/admin` routes
2. Missing or expired JWT → redirect to `/login`
3. Valid JWT with role=user → access to `/(workspace)` routes
4. Valid JWT with role=admin → access to both `/(workspace)` and `/admin` routes
5. Valid JWT with role=user attempting `/admin` → redirect to `/` with error
6. `/login` is accessible without authentication
7. `/api/auth/*` routes are accessible without authentication
8. All other `/api/*` routes require authentication (checked in individual route handlers)
9. Session persists across page refreshes within the same browser tab

## Technical Notes
- Use `NextResponse.next()` for allowed requests, `NextResponse.redirect()` for blocked
- Extract JWT from cookie in middleware, verify with `jose`
- Pass user info via request headers or cookies for downstream use
- `matcher` config: exclude static files, login page, auth API routes

## Files to Create/Modify
- `app/middleware.ts` (main middleware)
- `app/(workspace)/layout.tsx` (authenticated layout shell)
- `app/admin/layout.tsx` (admin layout shell)

## Testing
- Clear cookies, visit `/` — redirected to `/login`
- Login as user, visit `/` — workspace loads
- Login as user, visit `/admin` — redirected to `/`
- Login as admin, visit `/admin` — admin page loads
- Refresh page — session persists (no re-login)
