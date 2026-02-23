# Story 017: Inline Editing (Click-to-Edit All Fields)

**Epic**: E-4 (Document Preview & Editing)
**Requirements**: FR-16
**Dependencies**: Story 016
**Priority**: MUST

## Description
Make all point fields editable by clicking on them. The PM can edit subject content, title, for_whom, and due date directly within the document preview.

## Acceptance Criteria
1. Click on subject content → inline text editor (textarea) opens in place
2. Click on title → inline text input opens
3. Click on for_whom → inline text input opens
4. Click on due → inline text input opens
5. Edits saved to zustand store on blur (clicking outside) or pressing Enter
6. Escape key cancels the edit and reverts to previous value
7. Active editing field has a visible border/outline (e.g., blue border)
8. Non-editing state shows content as normal text (no input borders)
9. All edits persist in zustand store (survive scrolling up/down)

## Technical Notes
- Create a reusable `InlineEdit` component that toggles between display and edit mode
- For subject content (multi-line): use `<textarea>` with auto-resize
- For single-line fields (title, for_whom, due): use `<input type="text">`
- zustand actions: `updatePointContent(sectionIndex, pointIndex, field, value)`
- Only the proposed content is editable (existing grey content is read-only)

## Files to Create/Modify
- `components/document-preview/inline-edit.tsx` (reusable inline editor)
- `components/document-preview/point-row.tsx` (wrap fields with InlineEdit)
- `components/document-preview/point-content.tsx` (editable proposed content)
- `lib/store.ts` (add edit actions)

## Testing
- Click on a proposed subject line → textarea appears with content
- Edit text, click outside → text saved, display updated
- Press Escape → edit cancelled, original text restored
- Click on for_whom → input appears, edit, blur → saved
- Refresh check: edits persist in zustand (no re-fetch needed)
