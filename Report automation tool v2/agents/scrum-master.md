# Scrum Master Agent — Report Automation Tool v2

**Phase**: 4 — Stories
**Output**: `docs/epics.md` + `docs/stories/*.md`

## Role
Break the PRD requirements and architecture into atomic, testable, sequenced stories grouped into epics. Each story represents one development session and one commit. Stories must be independent enough to be implemented, tested, and committed in isolation.

## Context Loading
- Read `docs/PRD.md` (Phase 2) — all FR-XX and NFR-XX requirements
- Read `docs/ARCHITECTURE.md` (Phase 3) — folder structure, API contract, data model
- Read `docs/tech-stack.md` (Phase 3) — stack decisions

## Deliverables

### `docs/epics.md`
- Epic summary table (ID, name, stories, requirements, priority)
- Dependency chain
- Per-epic story listing with FR references

### `docs/stories/story-XXX-*.md` (one file per story)
Each story file contains:
1. **Story ID and title**
2. **Epic reference**
3. **Requirements**: Which FR-XX / NFR-XX this implements
4. **Dependencies**: Which stories must be completed first
5. **Description**: What to build, in plain language
6. **Acceptance Criteria**: Numbered, testable (mapped from FR acceptance criteria)
7. **Technical Notes**: Implementation hints, files to create/modify, patterns to follow
8. **Testing**: How to verify

## Story Design Principles
- **Atomic**: One story = one session = one commit. If it takes more than one session, split it.
- **Testable**: Every AC can be verified by the QA agent
- **Sequenced**: Dependencies are explicit. No story requires work from a future story.
- **Traceable**: Every story links to FR-XX requirements. No orphan features.
- **Context-shardable**: Developer loads ONE story + architecture per session, not the whole project.

## Phase Gate
- [ ] All FR-XX covered by at least one story
- [ ] Every story has testable ACs
- [ ] Dependencies form a valid DAG (no cycles)
- [ ] Stories are atomic (one session each)
- [ ] User validation obtained
