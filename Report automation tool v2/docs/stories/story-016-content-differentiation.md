# Story 016: Content Differentiation (Existing vs Proposed)

**Epic**: E-4 (Document Preview & Editing)
**Requirements**: FR-15
**Dependencies**: Story 015
**Priority**: MUST

## Description
Visually differentiate existing content (from previous meetings) and proposed new content (from AI analysis) within each point.

## Acceptance Criteria
1. Existing content (previous meetings) displayed in normal weight, muted grey color
2. Proposed new content (from AI for this meeting) displayed in bold, with a subtle highlight background (e.g., light yellow or light blue)
3. New points have a distinct "NEW" badge or colored left border
4. For updated points: existing content visible above the proposed addition
5. Point updates show: [existing grey content] → [proposed bold content] clearly separated
6. Color coding is consistent across all sections
7. Visual distinction works without relying solely on color (bold + background)

## Technical Notes
- `PointContent` component splits rendering between existing paragraphs and proposed paragraphs
- Existing paragraphs: `has_bold: false` → grey text, normal weight
- Existing paragraphs: `has_bold: true` → these were "new" in the PREVIOUS meeting, now demoted
- Proposed content (from `pointUpdates[].subject_lines`): bold + highlight
- New points: entire content is highlighted + "NEW" badge on the row

## Files to Create/Modify
- `components/document-preview/point-content.tsx` (split existing/proposed rendering)
- `components/document-preview/point-row.tsx` (add NEW badge for new points)
- Tailwind classes for muted/highlight styles

## Testing
- Existing points without updates: all grey/normal text
- Existing points WITH updates: grey text followed by highlighted bold proposal
- New points: entire row has highlight + NEW badge
- Visual distinction is clear at a glance
