# Story 009: First Report Mode (Template Selector)

**Epic**: E-2 (Python Backend & File Upload)
**Requirements**: FR-06
**Dependencies**: Story 007
**Priority**: MUST

## Description
Add a toggle for "First report (use template)" mode. When selected, the .docx upload is replaced by a template selector that loads a template from Supabase Storage.

## Acceptance Criteria
1. Toggle or switch: "Update existing report" (default) vs "First report (use template)"
2. When "First report" selected, .docx upload zone is hidden
3. Template selector appears showing available templates from Supabase
4. At least the main Immo-Pro template is listed (seeded in Story 002)
5. Default template is pre-selected
6. Selected template is fetched from Supabase Storage as bytes
7. Template is parsed using the same `parse-report` endpoint
8. Parsing summary correctly shows "N°0 — blank template" indication
9. Transcript upload remains required in both modes

## Technical Notes
- `GET /api/templates` fetches template list from Supabase `templates` table
- Template .docx downloaded from Supabase Storage (server-side, not client)
- Pass template bytes to `parse-report` endpoint same as uploaded file
- Store `mode: 'update' | 'first_report'` in zustand

## Files to Create/Modify
- `app/(workspace)/page.tsx` (add mode toggle)
- `app/api/templates/route.ts` (GET: list templates)
- `lib/store.ts` (add mode state)
- `components/template-selector.tsx` (template picker component)

## Testing
- Toggle to "First report" → .docx upload hidden, template selector shown
- Select main template → parsed as blank template (0 points, sections detected)
- Toggle back to "Update existing" → .docx upload shown again
- Upload transcript + select template → both files ready for analysis
