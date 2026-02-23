# Story 008: Transcript Upload + Parse-Transcript Endpoint

**Epic**: E-2 (Python Backend & File Upload)
**Requirements**: FR-05, FR-08
**Dependencies**: Story 006
**Priority**: MUST

## Description
Build the file upload UI for the .txt transcript and the Python endpoint that cleans and structures it.

## Acceptance Criteria
1. Upload zone for .txt displayed alongside the .docx upload (labeled "Transcript")
2. Drag-and-drop and click-to-browse work for .txt files
3. Only .txt files accepted
4. File size limit: 10 MB
5. `POST /api/parse-transcript` accepts text body, returns cleaned transcript + stats
6. Auto-detects Leexi format (speaker + timestamp) vs plain text
7. Leexi: turns parsed, noise removed, consecutive same-speaker merged
8. Plain text: paragraphs extracted, header/attendance parsed
9. Stats returned: raw turns, noise removed, after cleaning, after merging, duration
10. Both example transcripts in `Examples/` parse correctly

## Technical Notes
- Frontend reads .txt as text (`FileReader.readAsText`), sends as plain text body
- Python endpoint: `clean_transcript(text)` + `format_clean_transcript(result)`
- Return both structured result and formatted text
- Store in zustand store (`cleanedTranscript`, `cleanedText`)

## Files to Create/Modify
- `app/(workspace)/page.tsx` (add transcript upload zone)
- `api/parse-transcript.py` (Python endpoint)
- `lib/store.ts` (add transcript state)
- `components/file-uploader.tsx` (reuse, configure for .txt)

## Testing
- Upload `leexi-20260115-transcript-penta_update_siamu.txt` → Leexi format detected, turns parsed
- Upload `leexi-20260121-transcript-penta_phase_2_sprinklage.txt` → same
- Upload a plain text meeting notes file → plain text format detected
- Stats display correct numbers
