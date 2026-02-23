# Story 015: Point Rows (Number, Title, Content, ForWhom, Due)

**Epic**: E-4 (Document Preview & Editing)
**Requirements**: FR-14
**Dependencies**: Story 014
**Priority**: MUST

## Description
Render each point within its section as a table-like row with all fields: number, title, subject content, for_whom, and due date.

## Acceptance Criteria
1. Each point rendered as a row within its section (table-like layout with columns)
2. Point number displayed in first column (e.g., "01.01", "07.03")
3. Point title displayed in second column
4. Subject content displayed in third column (multi-line, preserving paragraph structure)
5. For_whom displayed in fourth column
6. Due date/status displayed in fifth column
7. Column widths proportional: narrow (N°, Title, ForWhom, Due), wide (Subject)
8. Points ordered by their number within each section
9. Both existing points (from previous report) and new points (from AI) rendered

## Technical Notes
- `PointRow` component receives point data from zustand store
- Existing points: show all historical paragraphs (from parsed report)
- New points (from AI): show proposed content
- CSS grid or table layout for consistent column alignment
- Subject paragraphs: map over `subject_paragraphs[]` array, one `<p>` per paragraph

## Files to Create/Modify
- `components/document-preview/point-row.tsx`
- `components/document-preview/section-block.tsx` (render points within section)

## Testing
- Upload Penta N12 → analyze → review shows all points in correct sections
- Each point shows number, title, content, for_whom, due
- Multi-paragraph subjects render as separate lines
- New points from AI appear in their assigned sections
