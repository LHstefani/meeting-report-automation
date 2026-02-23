# Story 018: Metadata Panel (Editable, Fixed Position)

**Epic**: E-4 (Document Preview & Editing)
**Requirements**: FR-17
**Dependencies**: Story 014
**Priority**: MUST

## Description
Build the metadata panel at the top of the review page with editable fields for meeting number, dates, and next meeting info.

## Acceptance Criteria
1. Metadata panel displayed at the top of the review page (above the document preview)
2. Panel is visually distinct (card or sticky header)
3. Editable fields: meeting number (numeric), date (DD/MM/YYYY), distribution date, next meeting date, next meeting time
4. Meeting number populated from AI proposal (previous + 1)
5. Date populated from AI proposal (extracted from transcript)
6. Changes immediately reflected in the document preview header
7. Date inputs accept DD/MM/YYYY format (text input with format hint)
8. Panel stays accessible while scrolling the document (sticky or always visible)

## Technical Notes
- zustand: `metadata` object with all fields, `updateMetadata(field, value)` action
- Panel could be sticky (`position: sticky; top: 0`) or in a sidebar
- shadcn/ui `Input` for text fields, `Input type="number"` for meeting number
- Two-column layout for compact display

## Files to Create/Modify
- `components/document-preview/metadata-panel.tsx`
- `app/(workspace)/page.tsx` (add panel above document preview)
- `lib/store.ts` (metadata state + actions)

## Testing
- Metadata fields show AI-proposed values
- Change meeting number → document header updates
- Change date → document header updates
- Scroll down in document → metadata panel stays visible
