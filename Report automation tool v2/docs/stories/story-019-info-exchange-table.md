# Story 019: Info Exchange Table (Editable, Add/Delete Rows)

**Epic**: E-4 (Document Preview & Editing)
**Requirements**: FR-18
**Dependencies**: Story 014
**Priority**: MUST

## Description
Render the info exchange table within the document preview with editable cells and the ability to add/delete rows.

## Acceptance Criteria
1. Info exchange table displayed in the document flow (after subject sections)
2. Table columns: From, Status, Content, Due Date
3. Each cell is editable on click (inline edit)
4. "Add row" button below the table
5. Each row has a delete button (icon or X)
6. Empty rows are visually distinct (placeholder text)
7. Data sourced from zustand store (populated from AI proposals)
8. Edits, additions, and deletions persist in store

## Technical Notes
- Reuse `InlineEdit` component from Story 017
- zustand: `infoExchange[]` array with CRUD actions
- Table styling should match the document aesthetic (not shadcn DataTable)
- Delete confirmation not needed (can undo by adding back)

## Files to Create/Modify
- `components/document-preview/info-exchange-table.tsx`
- `components/document-preview/document-preview.tsx` (add info exchange section)
- `lib/store.ts` (info exchange CRUD actions)

## Testing
- Info exchange items from AI displayed in table
- Click a cell → edit inline → value saved
- Click "Add row" → empty row appears
- Click delete on a row → row removed
- Multiple edits persist
