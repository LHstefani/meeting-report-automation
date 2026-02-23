# Story 026: Generate-Report Endpoint (BytesIO, Bold Management)

**Epic**: E-7 (Report Generation & Download)
**Requirements**: FR-28, FR-29
**Dependencies**: Story 006, Story 014
**Priority**: MUST

## Description
Build the `/api/generate-report` Python endpoint that takes the edited proposal state and generates a .docx file in-memory using BytesIO, preserving template formatting and applying bold management rules.

## Acceptance Criteria
1. `POST /api/generate-report` accepts: edited proposal JSON + original report/template file (as base64 or multipart)
2. Output is a valid .docx file returned as binary response (application/octet-stream)
3. Template formatting fully preserved: fonts, colors, header/logo, table styles, cell widths, page layout
4. Previous meeting content is un-bolded (bold runs → normal weight)
5. New/updated content for this meeting is bold
6. New point rows match the exact table structure of existing points (cloned row approach)
7. Metadata updated in document: meeting number, date, distribution date, next meeting info
8. Info exchange table reflects the edited state (added/removed/modified rows)
9. Planning table reflects the edited state (added/removed/modified items)
10. Rejected point updates are excluded (existing content stays as-is)
11. Removed new points are excluded
12. Point numbering in the document matches the auto-numbered state from the editor
13. Filename suggestion returned in response header: `Content-Disposition: attachment; filename="..."`
14. Filename follows convention: preserve project prefix, update N-number and date (YYYYMMDD)

## Technical Notes
- Python function: `api/generate-report.py`
- Reuses `src/report_generator.py` with BytesIO adaptation:
  - Input: `Document(BytesIO(base64_decoded_bytes))` instead of file path
  - Output: `doc.save(output_buffer)` where `output_buffer = BytesIO()`
  - Return `output_buffer.getvalue()` as response body
- Key functions from v1 to adapt:
  - `unbold_all_content()` — un-bold all runs in subject tables
  - `update_existing_point()` — add new subject line in bold below existing
  - `add_new_point()` — clone last row, populate with new point data in bold
  - `clone_table_row()` — deep XML clone of table row for new points
- Bold management: uses `python-docx` run-level bold (`run.bold = True/False`) and lxml for deep XML manipulation
- Timeout: 10 seconds (Vercel standard function timeout)

## Files to Create/Modify
- `api/generate-report.py` (new Python serverless function)
- `src/report_generator.py` (adapt for BytesIO input/output, accept JSON state instead of raw AI output)

## Testing
- Generate report from update mode → .docx opens correctly in Word
- Previous content is NOT bold, new content IS bold
- New points have correct table row structure (same cells, same widths)
- Metadata in header matches edited values
- Info exchange table in .docx matches edited state
- Planning section in .docx matches edited state
- Rejected updates not present in output
- Removed new points not present in output
- Filename in response header follows convention (e.g., `Penta_MoM-PV N13 20260211.docx`)
