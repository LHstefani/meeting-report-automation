# Story 022: Quality Check Endpoint (Q1-Q10 Logic)

**Epic**: E-5 (Quality Analysis)
**Requirements**: FR-22, FR-23, FR-24
**Dependencies**: Story 014
**Priority**: MUST

## Description
Build the `/api/quality-check` Python endpoint that evaluates the current report state against 10 quality criteria (Q1-Q4 blocking, Q5-Q10 warnings) and returns a structured result.

## Acceptance Criteria
1. `POST /api/quality-check` accepts the full report state (metadata, sections, points, info exchange, planning) as JSON
2. Q1 — All metadata filled: meeting number, date, distribution date, next meeting date all present and non-empty
3. Q2 — Report number integrity: equals previous + 1, or equals 1 for first report mode
4. Q3 — Content exists: at least one new point OR one modified point with accepted status
5. Q4 — Bold formatting: all accepted new/modified content is marked for bold output
6. Q5 — No duplicate point numbers across all sections
7. Q6 — Content language matches report language (simple heuristic: majority word detection FR/NL/EN)
8. Q7 — New point titles are 2-5 words (not too short/long)
9. Q8 — Subject content is at least one meaningful sentence per accepted point
10. Q9 — Info exchange items have both status and due date filled
11. Q10 — Report date is plausible (not > 30 days in the past, not in the future)
12. Response JSON: `{ "score": 8, "total": 10, "blocking_pass": true/false, "checks": [...] }`
13. Each check object: `{ "id": "Q1", "label": "...", "category": "blocking"|"warning", "passed": bool, "message": "..." }`
14. Q1-Q4 failures → `blocking_pass: false` (download blocked)
15. Q5-Q10 failures → warnings only (download allowed)

## Technical Notes
- Python function: `api/quality-check.py`
- Stateless: receives full state in request body, returns quality result
- Language detection for Q6: use simple word-frequency heuristic (common FR/NL/EN words), no external library needed
- Q4 (bold check): verify that every accepted point_update and new_point has `is_bold: true` or equivalent flag — this is a structural check on the data, not on actual .docx formatting
- Response time target: < 2 seconds (no AI call, pure logic)

## Files to Create/Modify
- `api/quality-check.py` (new Python serverless function)
- `src/quality_checker.py` (new module with Q1-Q10 logic, imported by the endpoint)

## Testing
- Submit report state with all metadata filled → Q1 passes
- Submit report state with missing date → Q1 fails, blocking_pass = false
- Meeting number = previous + 1 → Q2 passes
- Meeting number = previous + 3 → Q2 fails
- No accepted points → Q3 fails (blocking)
- Duplicate point numbers → Q5 warns
- Title with 1 word → Q7 warns
- Title with 4 words → Q7 passes
- Date 60 days ago → Q10 warns
- All 10 pass → score = 10, blocking_pass = true
