# Story 011: AI Analysis Endpoint + Loading UX

**Epic**: E-3 (AI Analysis)
**Requirements**: FR-10, FR-11
**Dependencies**: Story 010
**Priority**: MUST

## Description
Build the AI analysis endpoint that sends the parsed report + cleaned transcript to Claude API and returns structured update proposals. Add loading UX for the 30-60 second analysis.

## Acceptance Criteria
1. `POST /api/analyze` accepts parsed report JSON + cleaned transcript text
2. Endpoint uses Anthropic API key from env var (never from client)
3. AI returns structured JSON: meeting_number, date, point_updates, new_points, info_exchange, planning
4. JSON is validated before returning (retry once if invalid)
5. For update mode: existing points discussed get update proposals, new topics become new points
6. AI uses the same language as the report
7. Loading state shown with message: "Analyzing transcript... ~30-60 seconds"
8. Progress animation/spinner visible during analysis
9. Error state shown if API call fails, with retry button
10. Proposals stored in zustand after successful analysis
11. After analysis, automatically transition to review step

## Technical Notes
- Reuse `ai_analyzer.py` with `analyze_meeting()` function
- API key: `os.environ['ANTHROPIC_API_KEY']` in Python function
- Frontend: call `/api/analyze` with fetch, handle loading/error states
- Request body: `{ parsed_report: {}, cleaned_text: "" }`
- Python function handles both the API call and validation
- System prompt: reuse `SYSTEM_PROMPT_UPDATE` from v1

## Files to Create/Modify
- `api/analyze.py` (Python endpoint)
- `app/(workspace)/page.tsx` (trigger analysis, loading state)
- `lib/store.ts` (add proposals state, step transition)
- `components/analysis-loading.tsx` (loading/progress component)

## Testing
- Upload Penta N12 + Leexi transcript → click Analyze → proposals appear after 30-60s
- Check proposals contain point_updates and new_points
- Proposals language matches report language (English for Penta)
- Network error → error message shown with retry button
- Retry → analysis re-runs
