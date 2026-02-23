# Story 027: Download UI + Filename + Quality Gate + Reset

**Epic**: E-7 (Report Generation & Download)
**Requirements**: FR-29, FR-30
**Dependencies**: Story 026, Story 022
**Priority**: MUST

## Description
Build the download section of the UI: the generate/download button with quality gate enforcement, filename preview, warning acknowledgment, and workspace reset after download.

## Acceptance Criteria
1. "Generate Report" button prominently displayed at the bottom of the review page
2. Button triggers quality check before generation (re-runs `/api/quality-check`)
3. If blocking criteria (Q1-Q4) fail: button disabled, red message listing what must be fixed
4. If only warnings (Q5-Q10): button enabled, yellow summary shown, user can proceed
5. Clicking the button calls `/api/generate-report` with the current edited state
6. Loading state during generation: button shows spinner + "Generating..."
7. On success: browser file download triggered automatically
8. Filename preview shown near the button (e.g., "Will generate: `Penta_MoM-PV N13 20260211.docx`")
9. Filename auto-generated: project prefix preserved, N-number updated, date updated (YYYYMMDD format)
10. After successful download: "Start new report" button appears
11. "Start new report" resets the entire workspace (zustand store cleared, back to upload step)
12. Error during generation: error toast with retry option
13. Generation logged to Supabase (if Story 029 is implemented, otherwise deferred)

## Technical Notes
- Component: `components/download/download-section.tsx`
- Quality gate: call quality check endpoint, check `blocking_pass` before enabling generate
- File download: use `fetch` to call `/api/generate-report`, then create a Blob URL and trigger download via a hidden `<a>` element
- Filename construction: extract project prefix from original filename, format as `{prefix} N{meetingNum} {YYYYMMDD}.docx`
- Reset: zustand `resetWorkspace()` action that clears all state back to initial
- Step indicator: after download, move to final "Complete" step

## Files to Create/Modify
- `components/download/download-section.tsx` (new component)
- `app/(workspace)/page.tsx` (add download section to layout)
- `lib/store.ts` (add `resetWorkspace()` action, `originalFilename` state for filename construction)

## Testing
- All quality checks pass → "Generate Report" button enabled
- Q1 fails → button disabled, message "Missing metadata: date"
- Q7 warns → button enabled, yellow warning shown
- Click generate → loading spinner → file downloads
- Downloaded file opens correctly in Word
- Filename matches expected convention
- Click "Start new report" → workspace resets to upload step
- API error → error toast, button re-enabled for retry
