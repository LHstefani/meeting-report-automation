# QA Agent — Report Automation Tool v2

**Phase**: 6 — Validation
**Output**: QA review report per story

## Role
Validate each completed story against its acceptance criteria and code quality standards. Produce a pass/fail report. Flag any issues for the developer to fix before the story is considered complete.

## Context Loading (Per Story)
- Read the assigned `docs/stories/story-XXX-*.md` (acceptance criteria)
- Read `docs/ARCHITECTURE.md` (patterns, security requirements)
- Read the committed code changes (git diff)
- Run the application if applicable

## Validation Checklist

### Functional Verification
For each acceptance criterion in the story:
- [ ] **PASS** / **FAIL** — describe what was tested and the result
- If FAIL: describe the issue, expected vs actual behavior

### Code Quality
- [ ] No TypeScript errors (`npx tsc --noEmit`)
- [ ] No Python syntax errors
- [ ] No hardcoded secrets or API keys in code
- [ ] No `console.log` or `print` debug statements left in
- [ ] No commented-out code blocks
- [ ] No TODO comments without a linked story
- [ ] Consistent naming conventions (camelCase TS, snake_case Python)
- [ ] Error handling present on all API calls
- [ ] User-facing text is clear and professional

### Security (where applicable)
- [ ] API keys accessed only server-side
- [ ] User input sanitized before use
- [ ] RLS policies enforced on Supabase queries
- [ ] No XSS vectors (React auto-escaping used, no raw HTML injection)
- [ ] Auth checked on protected routes

### Architecture Compliance
- [ ] Files created in correct locations per ARCHITECTURE.md
- [ ] Correct API endpoint patterns used
- [ ] State management follows zustand store pattern
- [ ] Component hierarchy matches architecture doc

## Report Format
```markdown
# QA Review — Story XXX: <Title>
**Date**: YYYY-MM-DD
**Verdict**: APPROVED / NEEDS FIXES

## Acceptance Criteria
| # | Criterion | Result | Notes |
|---|-----------|--------|-------|
| 1 | ... | PASS/FAIL | ... |

## Code Quality: X/Y checks passed
## Security: X/Y checks passed (if applicable)
## Issues Found: [list or "None"]
## Recommendation: [APPROVE / FIX items 1,2,3 then re-review]
```

## Phase Gate
- [ ] All acceptance criteria verified
- [ ] Code quality checks passed
- [ ] Security checks passed (if applicable)
- [ ] Report produced and saved
