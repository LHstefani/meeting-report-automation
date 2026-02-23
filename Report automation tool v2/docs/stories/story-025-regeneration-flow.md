# Story 025: Re-Generation Flow + Updated Proposal Display

**Epic**: E-6 (Feedback & Re-Generation)
**Requirements**: FR-27
**Dependencies**: Story 024
**Priority**: MUST

## Description
Handle the full re-generation lifecycle: showing the transition from old to new proposal, preserving user edits where applicable, and managing the generation counter.

## Acceptance Criteria
1. When re-analysis starts, a semi-transparent overlay covers the document preview with "Re-analyzing..." text
2. Previous proposal remains visible (but dimmed) until the new one arrives
3. When new proposal arrives, document preview updates smoothly (no full page reload)
4. User's accept/reject decisions are reset to defaults (all accepted) on new proposal
5. User's manual edits are NOT preserved (new AI output replaces everything)
6. Generation counter displayed: "Generation 1 of N" / "Generation 2 of N" etc.
7. Generation counter increments each time re-analysis completes
8. If re-analysis fails (API error), previous proposal is restored with error toast
9. Feedback text area is cleared after successful re-analysis
10. Step indicator (from Story 010) stays on "Review" step during re-generation

## Technical Notes
- zustand: `generationCount: number` state, incremented on each successful re-analysis
- Transition: use React state to track `isRegenerating` boolean → controls overlay
- Error handling: wrap the re-analysis call in try/catch, restore previous state on failure
- The zustand `setAiProposal()` action handles clearing old data and setting new data atomically
- Toast notifications: use shadcn/ui `toast` for success/error feedback

## Files to Create/Modify
- `components/document-preview/document-preview.tsx` (add regeneration overlay)
- `components/feedback/feedback-panel.tsx` (add generation counter, clear on success)
- `lib/store.ts` (add `generationCount`, `isRegenerating` state + actions)

## Testing
- Click "Re-analyze with feedback" → overlay appears over document
- Previous proposal visible but dimmed under overlay
- New proposal arrives → overlay removed, document updated
- Generation counter shows "Generation 2"
- Accept/reject toggles reset to accepted
- API error → previous proposal restored, error toast shown
- Feedback text cleared after success
