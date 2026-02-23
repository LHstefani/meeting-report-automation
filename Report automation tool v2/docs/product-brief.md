# Product Brief — Immo-Pro Report Automation Tool v2

**Document**: Phase 1 — Discovery
**Author**: CTO Agent (Analyst role)
**Date**: 2026-02-23
**Status**: DRAFT — awaiting user validation

---

## 1. Vision Statement

A web-based meeting report automation platform that enables Immo-Pro Project Managers to generate professional meeting reports (PV/MoM) in minutes instead of hours, by combining AI-powered transcript analysis with an intuitive document-like editing interface.

---

## 2. Problem Statement

### Current Pain
Immo-Pro PMs manage multiple construction/real estate projects and must produce meeting reports (PV — procès-verbaux, or MoM — minutes of meeting) after every meeting. This process is:

1. **Time-consuming**: Each report takes 1-3 hours of manual work — reading transcripts, cross-referencing the previous report, writing updates, adding new points, updating metadata.
2. **Error-prone**: PMs may miss action items, forget to update responsible parties, or introduce inconsistencies in numbering and formatting.
3. **Inconsistent**: Different PMs deviate from the company template (renaming sections, removing columns), creating drift in report quality.
4. **Not scalable**: As project load increases, report writing becomes a bottleneck.

### Current Workaround (v1 MVP)
A Streamlit-based prototype was built and tested successfully. It demonstrates the core concept:
- Upload previous .docx report + .txt transcript
- AI analyzes and proposes updates
- PM reviews in a form-based interface (Streamlit tabs)
- Download new .docx report

**MVP validation**: The v1 was used on real projects (Penta N13, CORUM HC N01) and proved the concept works. However, the form-based editing is disconnected from the final document appearance, there is no authentication, and no quality assurance loop.

---

## 3. Target Users

### Primary: Immo-Pro Project Managers (5-10 users)
- **Technical level**: Low — comfortable with Word, email, and web browsers. No coding skills.
- **Frequency**: 2-10 reports per week across all PMs.
- **Languages**: French (primary), English, Dutch — reports can be in any of these.
- **Context**: Construction site meetings, technical coordination, client meetings, workshops.
- **Devices**: Laptop/desktop (office + site). No mobile requirement.

### Secondary: Immo-Pro Management
- Visibility into report quality and consistency across projects.
- Not direct users of the tool.

---

## 4. Proposed Solution

A **Next.js web application** (hosted on Vercel) with **Supabase** backend and **Anthropic Claude API** for AI analysis. The application replaces the Streamlit MVP with a production-grade tool featuring:

### Core Workflow (4 steps)

```
[1. UPLOAD]          [2. AI ANALYSIS]         [3. REVIEW & EDIT]        [4. DOWNLOAD]
PM uploads           AI compares              Document-like preview      PM downloads
.docx + .txt    -->  transcript vs        --> with inline editing   --> final .docx
                     previous report          of proposed content        report
```

### Key Differentiators vs MVP

| Capability | MVP (v1) | Production (v2) |
|-----------|----------|-----------------|
| UI editing | Form fields in tabs | Document-like preview with inline editing |
| Authentication | None | Email allowlist |
| Quality check | None | Automated quality analysis loop |
| Feedback loop | None | User feedback → AI re-generation |
| First report | Template-based | Template-based (keep) |
| Deployment | Local only | Shared URL (Vercel) |
| Multi-project support | Per-session only | History/project tracking |

---

## 5. Core Features

### F1 — Email-Based Authentication
- PM accesses the tool via a shared URL
- Login screen: PM enters their email address
- Email checked against an admin-managed allowlist stored in Supabase
- Approved emails get access; others see "Contact your administrator"
- Lightweight — no password management, no SSO complexity
- Admin interface to manage the allowlist (add/remove emails)

### F2 — File Upload & Parsing
- Upload previous .docx report (or select template for first report)
- Upload .txt transcript (Leexi, Teams, Plaud, manual notes, or mixed)
- Auto-detect report format (Penta, CORUM, Quartier Numérique, or new projects using the standard template)
- Auto-detect transcript format (Leexi with timestamps, or plain text)
- Display parsing summary (sections found, points count, transcript duration/length)

### F3 — AI-Powered Transcript Analysis
- Send parsed report structure + cleaned transcript to Claude API
- AI identifies: point updates, new points, info exchange items, planning items, metadata
- Two modes: update existing report (incremental) or create first report from template
- Structured JSON output validated before presenting to user
- Show cost estimate after analysis

### F4 — Document-Like Preview & Inline Editing
- Render the report proposal as an HTML document that visually resembles the final Word output
- Sections displayed in order with proper headings
- Existing points shown with previous content (grey/normal) + proposed new content (highlighted/bold)
- New points shown with highlight indicator
- **Inline editing**: Click any point → edit content, title, responsible party, due date directly
- **Metadata panel**: Fixed sidebar/header with meeting number, date, distribution date, next meeting
- Attendance, info exchange, and planning tables editable within the document flow
- Add/remove points and info exchange rows
- Drag-to-reorder new points within sections

### F5 — Quality Analysis Loop
- After AI analysis (or after user edits), run an automated quality check
- Check against defined criteria (to be brainstormed — see Section 8)
- Display quality score and flagged issues
- User can fix issues and re-check
- Quality gate before download (warning, not blocking)

### F6 — User Feedback & AI Re-Generation
- After reviewing the AI proposal, PM can type feedback in a text field
- Examples: "Merge points 07.03 and 07.04", "The sprinkler topic was more about timeline than cost", "Add more detail on the kitchen discussion"
- Feedback sent to AI as a follow-up prompt with the current state
- AI re-generates affected parts (not the full report)
- PM reviews the updated proposal

### F7 — Report Generation & Download
- Generate final .docx from the edited proposal
- Preserve original template formatting (fonts, colors, header, logo, table styles)
- Bold management: un-bold previous meeting content, new content in bold
- Auto-increment meeting number and filename
- Auto-update dates in metadata and filename
- Download button with correct filename

### F8 — Template Management
- Store the main Immo-Pro template
- Support template variants (per project or PM preference)
- Allow PM to select which template to use for first reports
- Predefined section list for first report generation

### F9 — Usage Tracking (Admin)
- Log each report generation (who, when, which project, input files)
- Simple admin dashboard showing usage stats
- Helps Immo-Pro management understand adoption and ROI

---

## 6. Out of Scope (v2)

- Mobile-optimized interface (desktop only)
- Real-time collaboration (single PM per report)
- Integration with project management tools (Procore, etc.)
- Automatic meeting recording/transcription (PMs bring their own .txt)
- Multi-company support (Immo-Pro only)
- Versioning/history of individual reports (not tracked beyond generation log)

---

## 7. Success Metrics

| Metric | Target |
|--------|--------|
| Time per report | < 15 minutes (down from 1-3 hours) |
| Adoption | 80% of PMs using the tool within 1 month |
| Quality score | Average > 85% on quality checks |
| AI accuracy | < 20% of proposed content requires major edits |
| Uptime | 99%+ (Vercel + Supabase managed infra) |
| Cost per report | < $0.20 in AI API costs |

---

## 8. Open Items for Phase 2 Brainstorming

### Quality Criteria (F5) — User-Confirmed Base Criteria

These are the **mandatory base checks** — the minimum bar ensuring the tool produces valid output:

| # | Criterion | Type | Severity |
|---|-----------|------|----------|
| Q1 | All metadata fields are filled in (meeting number, date, distribution date, next meeting) | Completeness | BLOCK |
| Q2 | Report number is incremented by 1 (or is 1 for first report) | Integrity | BLOCK |
| Q3 | There are new points OR modified points (tool produced content, not nothing) | Content | BLOCK |
| Q4 | Modified and new points are formatted in bold | Formatting | BLOCK |

**Additional confirmed criteria** (warnings — flag but allow download):

| # | Criterion | Type | Severity |
|---|-----------|------|----------|
| Q5 | No duplicate point numbers | Integrity | WARN |
| Q6 | Content language matches report language | Consistency | WARN |
| Q7 | New point titles are 2-5 words (not too long/short) | Quality | WARN |
| Q8 | Subject content is at least 1 meaningful sentence per point | Quality | WARN |
| Q9 | Info exchange items have status and due date | Completeness | WARN |
| Q10 | Report date is plausible (not in the past, not far future) | Integrity | WARN |

**Design note**: Q1-Q4 are blocking (prevent download). Q5-Q10 are warnings (flag but allow download). User will add more criteria as the tool matures.

### Template Deviation Handling
PMs modify templates (remove sections, rename columns). The parser handles this today, but the v2 document preview needs to gracefully support variations. Needs design attention in Phase 3.

---

## 9. Technical Considerations

### Architecture Decision: Python Backend
The existing v1 codebase (4 Python modules, ~1,600 lines) does deep .docx XML manipulation using `python-docx` and `lxml`. This code is battle-tested on real projects. Rewriting in JavaScript/TypeScript would be:
- Risky (Node.js docx libraries are less mature for XML-level manipulation)
- Time-consuming (rewrite + re-test all edge cases)
- Unnecessary (the Python code works well)

**Proposed approach**: Keep the Python processing pipeline as a backend API (FastAPI or Vercel Python serverless functions) and build the Next.js frontend on top. The frontend handles auth, UI, and orchestration; the Python backend handles .docx parsing, AI analysis, and .docx generation.

### Deployment
- **Frontend**: Next.js on Vercel (free tier sufficient for 5-10 users)
- **Backend**: Python functions on Vercel (Python runtime) or separate service (Railway/Fly.io)
- **Database**: Supabase (email allowlist, usage logs, file storage for uploads)
- **AI**: Anthropic API (Claude Sonnet, ~$0.05-0.15 per report)

### Known Constraints
- Vercel Python functions: 250MB package limit, 60s timeout (Pro: 300s)
- AI analysis can take 30-60 seconds — needs loading UX
- .docx files must not be stored permanently (client data sensitivity)
- Budget: Keep OPEX under 50 EUR/month for 5-10 users

---

## 10. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| AI produces inaccurate updates | High | Medium | Quality loop + mandatory PM review + feedback re-run |
| Template variations break parser | Medium | Medium | Expand parser test coverage with all 10+ example reports |
| Python backend deployment complexity | Medium | Low | Vercel Python runtime or containerized service |
| PM adoption resistance | Medium | Low | Simple UX, training session, show time savings |
| API cost overrun | Low | Low | Usage tracking + cost display per report |
| Transcript quality varies widely | Medium | High | Robust cleaner + AI handles noisy input gracefully |

---

## 11. Assumptions

1. PMs have access to meeting transcripts in .txt format (from Leexi, Teams, Plaud, or manual notes)
2. PMs have the previous report in .docx format (or use the template for first reports)
3. The Immo-Pro template structure remains broadly consistent (sections, columns, metadata)
4. 5-10 users is sufficient for v2 — no multi-tenant or enterprise requirements
5. The existing Python parsing/generation code is reusable with minor adaptations
6. Desktop-only usage is acceptable (no mobile requirement)

---

## Phase Gate Checklist

- [x] Vision documented
- [x] Target users identified
- [x] Problem and current state described
- [x] Core features listed (F1-F9)
- [x] Out of scope defined
- [x] Success metrics proposed
- [x] Risks identified with mitigations
- [x] Technical considerations outlined
- [x] Open items flagged for Phase 2
- [ ] **User validation** — awaiting approval to proceed to Phase 2 (Requirements)
