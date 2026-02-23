# Story 013: Token Usage + Cost Display

**Epic**: E-3 (AI Analysis)
**Requirements**: FR-13
**Dependencies**: Story 011
**Priority**: SHOULD

## Description
After AI analysis completes, display the token usage and estimated cost in a non-intrusive info banner.

## Acceptance Criteria
1. After analysis, display input tokens and output tokens
2. Estimated cost calculated based on Claude Sonnet pricing
3. Displayed as an info banner (not a modal or blocking dialog)
4. Format: "Analysis complete — 2,450 input + 1,200 output tokens (~$0.08)"
5. Cost recalculated after feedback re-generation (cumulative)

## Technical Notes
- Token counts come from `usage` field in AI response (already returned by v1 code)
- Cost formula: `(input * 3 / 1_000_000) + (output * 15 / 1_000_000)` (Sonnet pricing)
- Store cumulative cost in zustand for re-generation tracking

## Files to Create/Modify
- `components/cost-display.tsx`
- `app/(workspace)/page.tsx` (add cost display after analysis)
- `lib/store.ts` (add usage/cost tracking)

## Testing
- Run analysis → cost banner appears with token counts
- Cost is reasonable (~$0.05-0.15 for typical reports)
- After re-generation, cost shows cumulative total
