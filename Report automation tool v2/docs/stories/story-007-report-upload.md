# Story 007: Report Upload + Parse-Report Endpoint

**Epic**: E-2 (Python Backend & File Upload)
**Requirements**: FR-05, FR-07
**Dependencies**: Story 006
**Priority**: MUST

## Description
Build the file upload UI for the .docx report and the Python endpoint that parses it into structured JSON.

## Acceptance Criteria
1. Upload zone for .docx displayed on the workspace page (labeled "Previous Report")
2. Drag-and-drop works for .docx files
3. Click-to-browse works (file picker filtered to .docx)
4. Only .docx files accepted (other formats rejected with error)
5. File size limit: 10 MB (error shown for larger files)
6. Uploaded file can be removed/replaced before proceeding
7. `POST /api/parse-report` accepts .docx binary, returns parsed JSON
8. Parsed JSON includes: metadata, attendance, info_exchange, planning, sections (with points), language, next_meeting
9. Report format auto-detected (Penta, CORUM, Quartier Numérique, standard template)
10. Parsing works for all 10+ example reports in `Examples/` directory

## Technical Notes
- Upload component: use shadcn/ui or a custom drag-and-drop zone
- Frontend sends .docx as binary in POST body (or multipart/form-data)
- Python endpoint: read body as bytes → `parse_report_from_bytes(BytesIO(body))`
- Return JSON response with parsed structure
- Store parsed result in zustand store

## Files to Create/Modify
- `components/file-uploader.tsx` (reusable upload component)
- `app/(workspace)/page.tsx` (add upload zone)
- `api/parse-report.py` (Python endpoint)
- `lib/store.ts` (zustand store — initial setup with parsedReport state)

## Testing
- Upload `Penta_MoM-PV N12 20260204.docx` → parsed JSON in console/state
- Upload `Quartier Numérique_Réunion urbanisme PV N03 20241107.docx` → parsed correctly
- Upload a .txt file → rejected
- Upload a 15MB file → rejected with error
- Drag a .docx file onto the zone → accepted
