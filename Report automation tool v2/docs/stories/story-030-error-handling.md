# Story 030: Error Handling + Loading States + Edge Cases

**Epic**: E-9 (Polish & Production)
**Requirements**: NFR-01, NFR-03
**Dependencies**: All E-0 through E-7 stories
**Priority**: MUST

## Description
Audit and harden all error handling across the application. Ensure every async operation has proper loading states, error messages, and recovery paths. Handle edge cases gracefully.

## Acceptance Criteria
1. Every API call has a try/catch with user-friendly error message (no raw error dumps)
2. Every async operation shows a loading indicator (spinner, skeleton, or progress text)
3. Network errors show: "Connection error. Please check your internet and try again." with retry button
4. API timeout errors show: "The operation took too long. Please try again." with retry button
5. File upload errors: invalid format → "Please upload a .docx file", too large → "File exceeds 5MB limit"
6. AI analysis timeout: "Analysis is taking longer than expected. Please try again." (90s timeout)
7. Supabase errors: generic "Something went wrong. Please try again." (no database details exposed)
8. Session expired: auto-redirect to login page with "Session expired. Please sign in again."
9. Empty transcript: "The transcript appears to be empty. Please check the file."
10. No points extracted by AI: "No discussion points were found in the transcript. Please verify the content."
11. Global error boundary catches unhandled React errors with recovery UI
12. All loading states meet NFR-01 performance targets (visible feedback within 200ms of action)
13. No blank screens on any error condition

## Technical Notes
- Create `components/ui/error-boundary.tsx` (React error boundary wrapper)
- Create `lib/errors.ts` with standardized error types and user-friendly messages
- Audit all `fetch()` calls in the app for missing error handling
- Add `React.Suspense` boundaries with skeleton fallbacks for lazy-loaded components
- Python endpoints: return structured error JSON `{ "error": "message", "code": "ERROR_CODE" }` with appropriate HTTP status codes
- Toast notifications for non-blocking errors (shadcn/ui `toast`)
- Full-screen error for blocking errors (error boundary)

## Files to Create/Modify
- `components/ui/error-boundary.tsx` (new global error boundary)
- `lib/errors.ts` (new error utilities)
- `app/error.tsx` (Next.js error page)
- `app/not-found.tsx` (Next.js 404 page)
- All Python endpoints in `api/*.py` (standardize error responses)
- All components with API calls (add/verify error handling)

## Testing
- Disconnect network → upload file → error message with retry
- Upload a .pdf instead of .docx → "Please upload a .docx file"
- Upload empty .docx → appropriate error message
- AI analysis times out → timeout message with retry
- Trigger Supabase error (e.g., RLS deny) → generic error, no DB details
- Navigate to invalid route → 404 page
- Force React render error → error boundary catches, recovery UI shown
