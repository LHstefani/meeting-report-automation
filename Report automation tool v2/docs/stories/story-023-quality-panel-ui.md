# Story 023: Quality Panel UI + Score Display

**Epic**: E-5 (Quality Analysis)
**Requirements**: FR-22, FR-24, FR-25
**Dependencies**: Story 022, Story 014
**Priority**: MUST (FR-22), SHOULD (FR-25)

## Description
Build the quality panel component that displays quality check results alongside the document preview. Shows pass/fail per criterion, overall score, and blocking vs. warning distinction.

## Acceptance Criteria
1. Quality panel displayed as a collapsible sidebar or card next to the document preview
2. Panel header shows overall score (e.g., "8/10 checks passed") with color indicator (green/yellow/red)
3. Blocking criteria (Q1-Q4) grouped under "Required" heading with red/green status icons
4. Warning criteria (Q5-Q10) grouped under "Warnings" heading with yellow/green status icons
5. Each criterion shows: status icon, label, and failure message if applicable
6. Failed blocking criteria highlighted with red background
7. Failed warnings highlighted with yellow background
8. "Re-check quality" button triggers a new quality check call
9. Quality check runs automatically after AI analysis completes (Story 011)
10. Quality check re-runs automatically before download attempt (Story 027)
11. Panel shows loading state during quality check
12. If all blocking criteria pass: green banner "Ready to generate"
13. If any blocking criteria fail: red banner "X issues must be resolved before generating"

## Technical Notes
- Component: `components/quality/quality-panel.tsx`
- Uses the `/api/quality-check` endpoint from Story 022
- zustand: store quality check results in `qualityResult` state
- Auto-trigger: call quality check after `setAiProposal()` action completes
- Re-check: call on button click, debounce to avoid rapid re-calls
- shadcn/ui: use `Badge`, `Card`, `Collapsible` components

## Files to Create/Modify
- `components/quality/quality-panel.tsx` (new component)
- `app/(workspace)/page.tsx` (add quality panel to layout)
- `lib/store.ts` (add `qualityResult` state + `setQualityResult` action)

## Testing
- Quality panel renders after AI analysis with correct score
- All passing → green "Ready to generate" banner
- Q1 fails → red banner, Q1 row highlighted red
- Q7 warns → yellow highlight, download still allowed
- Click "Re-check quality" → loading spinner → updated results
- Collapse/expand panel works
