# Story 010: Parsing Summary + Proceed to Analysis

**Epic**: E-2 (Python Backend & File Upload)
**Requirements**: FR-09
**Dependencies**: Stories 007, 008
**Priority**: MUST

## Description
After both files are uploaded and parsed, display a summary of the parsing results. User can proceed to AI analysis or go back to re-upload.

## Acceptance Criteria
1. Summary displayed after both files are parsed (not before)
2. Report summary shows: meeting number, date, section count, total point count, language detected
3. Transcript summary shows: format (Leexi/plain text), turn/paragraph count, duration (Leexi only)
4. If report is a blank template, clearly indicated: "First report — blank template (N°0)"
5. "Analyze" button enabled when both summaries are shown
6. "Back" or "Change files" option returns to upload step
7. Step indicator shows current progress (Upload → **Summary** → Review → Download)

## Technical Notes
- Summary data comes from zustand store (populated in Stories 007-009)
- Step indicator component: reusable across the workflow
- This is a UI-only story — no new backend endpoints

## Files to Create/Modify
- `components/parsing-summary.tsx`
- `components/step-indicator.tsx`
- `app/(workspace)/page.tsx` (add summary display + step flow)
- `lib/store.ts` (add step tracking)

## Testing
- Upload .docx + .txt → both parse → summary appears
- Summary shows correct metadata (check against known example reports)
- Click "Analyze" → proceeds to next step (analysis, built in Story 011)
- Click "Back" → return to upload step, can replace files
