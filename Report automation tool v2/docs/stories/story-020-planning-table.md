# Story 020: Planning Table (Editable, Add/Delete Items)

**Epic**: E-4 (Document Preview & Editing)
**Requirements**: FR-19
**Dependencies**: Story 014
**Priority**: MUST

## Description
Render the planning section within the document preview with editable items and add/delete capability.

## Acceptance Criteria
1. Planning section displayed in document flow (after info exchange)
2. Items displayed as a single-column list or table
3. Each item is editable on click
4. New items can be added via "Add item" button
5. Items can be deleted
6. New/modified items visually marked (bold indicator, matching Word convention)
7. Data sourced from zustand store (populated from AI proposals)

## Technical Notes
- Similar pattern to info exchange table but single column
- `is_new` flag determines bold styling
- zustand: `planning[]` array with CRUD actions

## Files to Create/Modify
- `components/document-preview/planning-table.tsx`
- `components/document-preview/document-preview.tsx` (add planning section)
- `lib/store.ts` (planning CRUD actions)

## Testing
- Planning items from AI displayed
- Existing items (not new) in normal weight
- New items in bold
- Click to edit → inline editor → save on blur
- Add/delete items works
