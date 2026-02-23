# Story 028: Template Management (Admin Upload, PM Selection)

**Epic**: E-8 (Templates & Usage Tracking)
**Requirements**: FR-31, FR-32
**Dependencies**: Story 002, Story 009
**Priority**: MUST (FR-31), COULD (FR-32)

## Description
Build admin template management (upload/replace templates in Supabase Storage) and enhance the PM's first-report mode with template selection when multiple templates exist.

## Acceptance Criteria
1. Admin page `/admin/templates` displays all stored templates
2. Each template shows: name, label, upload date, file size, default status
3. Admin can upload a new .docx template via file input
4. Upload stores the file in Supabase Storage `templates` bucket
5. Upload creates/updates the corresponding row in `templates` table (name, label, storage_path)
6. Admin can mark one template as default (`is_default = true`)
7. Admin can delete a template (with confirmation dialog)
8. PM template selector (from Story 009) fetches templates via `GET /api/templates`
9. Template list shows name and label for each available template
10. Default template is pre-selected in the selector
11. If only one template exists, selector is hidden (auto-selected)

## Technical Notes
- Admin page: `app/admin/templates/page.tsx`
- API routes: extend `app/api/templates/route.ts` with POST (upload) and DELETE methods
- Supabase Storage: upload to `templates/{filename}`, store path in `templates` table
- File validation: only accept .docx files, max 10MB
- Admin-only access: check user role in API route (same pattern as Story 005)
- shadcn/ui: use `Table`, `Button`, `Dialog` for the admin interface

## Files to Create/Modify
- `app/admin/templates/page.tsx` (new admin page)
- `app/api/templates/route.ts` (add POST and DELETE handlers)
- `components/upload/template-selector.tsx` (enhance from Story 009 to use API)
- `lib/store.ts` (add `selectedTemplate` state if not already present)

## Testing
- Admin uploads a .docx template → appears in list
- Admin marks template as default → default badge shown
- Admin deletes a template → removed from list (with confirmation)
- PM sees template selector with available templates
- Default template is pre-selected
- Single template → selector hidden
- Non-admin user cannot access /admin/templates
