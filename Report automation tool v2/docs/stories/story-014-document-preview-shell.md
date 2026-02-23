# Story 014: zustand Store + Document Preview Shell

**Epic**: E-4 (Document Preview & Editing)
**Requirements**: FR-14
**Dependencies**: Story 011
**Priority**: MUST

## Description
Set up the complete zustand store for report editing state and build the document preview shell — the paper-like container that renders the report structure with sections.

## Acceptance Criteria
1. zustand store fully defined with all editing state (metadata, pointUpdates, newPoints, infoExchange, planning)
2. Store populated from AI proposals when transitioning to review step
3. Document preview renders with paper-like appearance (white background, margins, max-width ~800px, subtle shadow)
4. Report header shown: project name, meeting number, date
5. Sections displayed in document order with section headings (styled as table headers)
6. Empty point placeholders shown per section ("X points in this section")
7. Scroll through the entire document naturally
8. Renders correctly on screens >= 1024px wide

## Technical Notes
- zustand store: single `useReportStore` with all state + actions (see ARCHITECTURE.md)
- Store hydrated from proposals: map `proposals.point_updates` → `pointUpdates[]` with `accepted: true`
- Document preview: CSS that mimics an A4 page (max-width, padding, font-family matching Word)
- Section headings: colored background bar matching the Word template style

## Files to Create/Modify
- `lib/store.ts` (complete zustand store definition)
- `lib/types.ts` (TypeScript interfaces for all report structures)
- `components/document-preview/document-preview.tsx` (main container)
- `components/document-preview/section-block.tsx` (section with heading)
- `components/document-preview/report-header.tsx` (project name, meeting info)
- `app/(workspace)/page.tsx` (render preview in review step)

## Testing
- Run analysis → transition to review → document preview appears
- Paper-like container visible with correct styling
- Section headings match the parsed report sections
- Scrollable document with proper margins
