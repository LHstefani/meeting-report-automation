# Story 024: Feedback Input + Analyze-Feedback Endpoint

**Epic**: E-6 (Feedback & Re-Generation)
**Requirements**: FR-26, FR-27
**Dependencies**: Story 011, Story 014
**Priority**: MUST

## Description
Add a feedback text area to the review screen and build the `/api/analyze-feedback` Python endpoint that sends user feedback + current state to Claude for re-analysis.

## Acceptance Criteria
1. Text area visible below the document preview with label "Feedback for AI"
2. Placeholder text with examples: "Merge points 07.03 and 07.04", "Add more detail about the facade works"
3. "Re-analyze with feedback" button next to the text area
4. Button disabled when feedback text is empty
5. `POST /api/analyze-feedback` accepts: original parsed report, transcript, current proposal state (with user edits), and feedback text
6. AI receives all context: original data + current edits + feedback as additional instruction
7. AI returns updated proposals in the same JSON structure as the initial analysis
8. Updated proposals replace the current preview (zustand store updated)
9. Previous proposal is NOT preserved (replaced by new one)
10. Loading state shown during re-analysis (same loading UX as Story 011)
11. After re-analysis, quality check re-runs automatically
12. Cost display updates with the new analysis cost (cumulative or per-call)
13. Re-analysis can be triggered multiple times (no limit)

## Technical Notes
- Python function: `api/analyze-feedback.py`
- Reuses `src/ai_analyzer.py` with an extended prompt that includes user feedback
- Add a new function: `analyze_with_feedback(parsed_report, transcript, current_state, feedback_text, api_key)`
- The feedback is appended as a user message after the initial analysis context
- Timeout: 90 seconds (same as initial analysis, Vercel Fluid Compute)
- zustand: `setFeedbackText(text)`, `clearFeedback()` actions

## Files to Create/Modify
- `components/feedback/feedback-panel.tsx` (new component: textarea + button)
- `api/analyze-feedback.py` (new Python serverless function)
- `src/ai_analyzer.py` (add `analyze_with_feedback()` function)
- `app/(workspace)/page.tsx` (add feedback panel to layout)
- `lib/store.ts` (add `feedbackText` state + actions)

## Testing
- Feedback text area renders below document preview
- Empty feedback → button disabled
- Type feedback + click button → loading state → updated proposal appears
- AI response respects feedback (e.g., "merge points" results in fewer points)
- Quality check re-runs after re-analysis
- Cost display updates
- Multiple re-analyses work without errors
