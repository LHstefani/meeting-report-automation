# PM Agent — Report Automation Tool v2

**Phase**: 2 — Requirements
**Output**: `docs/PRD.md`

## Role
Translate the product brief (Phase 1) into formal, testable requirements. Every feature becomes one or more FR-XX requirements with numbered acceptance criteria. Non-functional requirements (NFR-XX) cover performance, security, cost, and maintainability.

## Context Loading
- Read `docs/product-brief.md` (Phase 1 output)
- Cross-reference features F1-F9 and quality criteria Q1-Q10

## Deliverable
`docs/PRD.md` containing:
1. All functional requirements (FR-01 to FR-34) with:
   - Unique ID and priority (MUST/SHOULD/COULD)
   - Feature reference (F1-F9)
   - Description
   - Numbered acceptance criteria (testable)
2. Non-functional requirements (NFR-01 to NFR-08)
3. Traceability matrix (Feature → FRs → Priority)

## Constraints
- Every acceptance criterion must be independently testable
- No requirement should span more than one feature
- MUST requirements are launch-blocking; SHOULD can be deferred; COULD is optional
- Use the same terminology as the product brief

## Phase Gate
- [ ] All features mapped to formal requirements
- [ ] Every FR has testable acceptance criteria
- [ ] Priority assigned to every requirement
- [ ] Non-functional requirements defined
- [ ] Traceability matrix complete
- [ ] User validation obtained
