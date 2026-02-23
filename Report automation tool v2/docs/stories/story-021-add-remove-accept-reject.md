# Story 021: Add/Remove Points + Accept/Reject Toggles

**Epic**: E-4 (Document Preview & Editing)
**Requirements**: FR-20, FR-21
**Dependencies**: Story 017
**Priority**: MUST

## Description
Add controls to accept/reject AI-proposed updates, remove proposed new points, and manually add new points to any section.

## Acceptance Criteria
1. Each point update has an accept/reject toggle (default: accepted)
2. Rejected updates are visually dimmed (low opacity) and excluded from generation
3. Each new point has a "Remove" button or toggle
4. Removed new points are dimmed and excluded from generation
5. "Add point" button available at the bottom of each section
6. Clicking "Add point" creates an empty new point with editable fields (title, content, for_whom, due)
7. Manually added points require at least a title and content
8. Point numbering auto-adjusts: new points numbered as MeetingNum.01, .02, etc.
9. "Accept all" / "Reject all" bulk toggle available
10. Accept/reject state persists in zustand store

## Technical Notes
- Toggle component: simple checkbox or switch per point update
- zustand: `togglePointUpdate(index)`, `toggleNewPoint(index)`, `addNewPoint(sectionName)`, `removeNewPoint(index)`
- Auto-numbering: re-calculate numbers when points are added/removed, sorted by section order
- "Add point" opens an expanded row with empty fields in edit mode

## Files to Create/Modify
- `components/document-preview/point-row.tsx` (add toggle, remove button)
- `components/document-preview/section-block.tsx` (add "Add point" button)
- `components/document-preview/document-preview.tsx` (add bulk actions bar)
- `lib/store.ts` (toggle, add, remove actions + auto-numbering)

## Testing
- Toggle a point update to rejected → dimmed, excluded from count
- Toggle back to accepted → restored
- Remove a new point → dimmed
- Click "Add point" in a section → empty editable row appears
- Fill in title + content → point added to store
- Point numbers update correctly after additions/removals
- "Accept all" / "Reject all" works
