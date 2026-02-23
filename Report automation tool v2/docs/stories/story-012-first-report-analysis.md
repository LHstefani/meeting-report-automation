# Story 012: First Report Analysis Mode

**Epic**: E-3 (AI Analysis)
**Requirements**: FR-12
**Dependencies**: Story 011
**Priority**: MUST

## Description
Add the first-report analysis mode where the AI generates all content from scratch based on a template and transcript.

## Acceptance Criteria
1. When mode is "first_report", analysis uses `SYSTEM_PROMPT_NEW_REPORT` instead of update prompt
2. AI returns: empty point_updates, all content as new_points
3. Points grouped by template section names
4. 8-20 meaningful points depending on transcript length
5. Meeting number set to 1
6. Info exchange and planning items generated from transcript
7. Language matches template language
8. Max tokens increased for first reports (8192 vs 4096 for updates)

## Technical Notes
- `ai_analyzer.py` already has `_is_template_report()` detection and separate prompts
- Pass `mode` from frontend to help the endpoint select correct behavior
- The `analyze.py` endpoint routes to correct prompt based on parsed report content

## Files to Create/Modify
- `api/analyze.py` (ensure first-report mode works)
- `lib/store.ts` (mode-aware analysis trigger)

## Testing
- Select "First report" → choose template → upload transcript → Analyze
- Proposals contain only new_points (no point_updates)
- Meeting number = 1
- Points are distributed across template sections
- Content is in the template's language
