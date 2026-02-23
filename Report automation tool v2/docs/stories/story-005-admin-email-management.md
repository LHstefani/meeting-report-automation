# Story 005: Admin Email Allowlist Management

**Epic**: E-1 (Authentication & Admin)
**Requirements**: FR-03
**Dependencies**: Story 004
**Priority**: MUST

## Description
Build the admin page for managing the email allowlist. Admin can view all allowed emails, add new ones, and remove existing ones.

## Acceptance Criteria
1. `/admin/emails` page shows a table of all allowed emails (email, display_name, role, created_at)
2. "Add email" button opens a form/dialog with email + display_name + role (admin/user) inputs
3. Submitting the form adds the email to `allowed_emails` table
4. Each row has a "Remove" button that deletes the email from the table
5. Cannot remove your own admin email (prevent self-lockout)
6. Changes take effect immediately (new user can log in right away)
7. Only accessible to admin users (enforced by middleware + API route checks)
8. `GET /api/admin/emails` returns all emails (admin only)
9. `POST /api/admin/emails` adds email (admin only)
10. `DELETE /api/admin/emails` removes email by id (admin only)

## Technical Notes
- Admin API routes: verify JWT role=admin before processing
- Use Supabase service role client for admin operations (bypass RLS)
- Table component: shadcn/ui `Table` or `DataTable`
- Dialog: shadcn/ui `Dialog` for add form
- Optimistic UI: update table immediately, revert on error

## Files to Create/Modify
- `app/admin/emails/page.tsx`
- `app/api/admin/emails/route.ts` (GET, POST, DELETE)
- `components/admin/email-list.tsx`

## Testing
- Login as admin, navigate to `/admin/emails`
- See the seeded admin email in the table
- Add a new email — appears in the table
- Remove the new email — disappears from the table
- Try to remove own admin email — error/prevention
- Login as the newly added email — access granted
