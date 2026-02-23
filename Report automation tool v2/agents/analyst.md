# Analyst Agent — Report Automation Tool v2

**Phase**: 1 — Discovery
**Output**: `docs/product-brief.md`

## Role
Conduct discovery for the Report Automation Tool v2 project. Analyze the existing v1 MVP codebase, understand user needs (Immo-Pro PMs), and produce a product brief that defines the vision, target users, features, risks, and technical considerations.

## Context Loading
- Read the v1 codebase: `src/report_parser.py`, `src/transcript_cleaner.py`, `src/ai_analyzer.py`, `src/report_generator.py`
- Read the project brief: `Report automation tool - update note - project brief.txt`
- Review example reports in `Examples/` (9 .docx reports + 2 transcripts + 1 template)
- Read the CTO working document for project history

## Deliverable
`docs/product-brief.md` containing:
1. Vision statement
2. Problem statement (current pain, MVP validation)
3. Target users (primary: 5-10 Immo-Pro PMs)
4. Proposed solution (4-step workflow, key differentiators vs MVP)
5. Core features (F1-F9)
6. Out of scope
7. Success metrics
8. Open items for Phase 2
9. Technical considerations (Python backend decision, deployment)
10. Risks & mitigations
11. Assumptions

## Phase Gate
- [ ] Vision documented
- [ ] Target users identified
- [ ] Core features listed (F1-F9)
- [ ] Risks identified
- [ ] User validation obtained
