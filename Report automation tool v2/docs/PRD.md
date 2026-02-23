# Product Requirements Document (PRD) — Immo-Pro Report Automation Tool v2

**Document**: Phase 2 — Requirements
**Author**: CTO Agent (PM role)
**Date**: 2026-02-23
**Status**: DRAFT — awaiting user validation
**Source**: `docs/product-brief.md` (Phase 1 — Discovery)

---

## 1. Document Purpose

This PRD defines all functional and non-functional requirements for the Report Automation Tool v2. Every requirement is traceable to a feature (F1-F9) from the product brief and has testable acceptance criteria.

**Requirement ID format**: `FR-XX` (functional) / `NFR-XX` (non-functional)
**Priority**: MUST (required for launch) / SHOULD (important, can defer) / COULD (nice-to-have)

---

## 2. Functional Requirements

### 2.1 Authentication (F1)

#### FR-01: Email Login Screen
**Priority**: MUST
**Description**: The application displays a login screen where the PM enters their email address to access the tool. No password is required.

**Acceptance Criteria**:
1. Login page is the default view for unauthenticated users
2. Single email input field with "Sign in" button
3. Immo-Pro logo displayed on the login page
4. Invalid email format shows inline validation error
5. After successful login, user is redirected to the main workspace

#### FR-02: Email Allowlist Validation
**Priority**: MUST
**Description**: The entered email is checked against an admin-managed allowlist in Supabase. Only approved emails gain access.

**Acceptance Criteria**:
1. Email lookup is case-insensitive
2. Approved email → session created, redirect to workspace
3. Non-approved email → error message: "Access denied. Contact your administrator at [admin email]."
4. Allowlist is stored in a Supabase table (`allowed_emails`)
5. Lookup completes in < 1 second

#### FR-03: Admin Allowlist Management
**Priority**: MUST
**Description**: An admin user can add/remove emails from the allowlist.

**Acceptance Criteria**:
1. Admin view accessible only to users with `role = admin` in the allowlist table
2. Admin can add a new email to the allowlist
3. Admin can remove an email from the allowlist
4. Admin can see the full list of allowed emails with their role (admin/user)
5. Changes take effect immediately (no cache delay)

#### FR-04: Session Persistence
**Priority**: MUST
**Description**: Once logged in, the PM stays authenticated for the browser session. No re-login needed when navigating between pages.

**Acceptance Criteria**:
1. Session persists across page refreshes within the same browser tab
2. Session expires after 24 hours of inactivity
3. "Sign out" button available in the header/sidebar
4. After sign-out, user is redirected to the login page

---

### 2.2 File Upload & Parsing (F2)

#### FR-05: File Upload Interface
**Priority**: MUST
**Description**: The PM uploads two files: a previous meeting report (.docx) and a meeting transcript (.txt).

**Acceptance Criteria**:
1. Two upload zones clearly labeled: "Previous Report (.docx)" and "Transcript (.txt)"
2. Drag-and-drop supported for both zones
3. Click-to-browse supported for both zones
4. Only .docx accepted for report, only .txt accepted for transcript
5. File size limit: 10 MB per file
6. Upload progress indicator shown for large files
7. Uploaded files can be removed/replaced before analysis

#### FR-06: First Report Mode
**Priority**: MUST
**Description**: When creating the first report for a new project, the PM selects a template instead of uploading a previous report.

**Acceptance Criteria**:
1. Toggle or option: "First report (use template)" vs "Update existing report"
2. When "First report" is selected, the .docx upload is replaced by a template selector
3. At minimum, the main Immo-Pro template is available
4. Template file is stored server-side (not uploaded each time)
5. Transcript upload remains required in both modes

#### FR-07: Report Parsing
**Priority**: MUST
**Description**: The uploaded .docx report is parsed into a structured JSON representation, extracting metadata, sections, points, attendance, info exchange, and planning.

**Acceptance Criteria**:
1. Metadata extracted: meeting number, date, location, distribution date
2. Attendance table parsed (organizations, people, status)
3. Info exchange table parsed (from, status, content, due date)
4. Planning table parsed (content, bold status)
5. All subject sections detected with correct section names
6. All points extracted with: number, title, subject paragraphs (with bold tracking), for_whom, due
7. Language auto-detected (FR/EN/NL)
8. Parsing works for all 10+ example reports without errors
9. Next meeting info extracted from document paragraphs

#### FR-08: Transcript Parsing
**Priority**: MUST
**Description**: The uploaded .txt transcript is cleaned and structured, supporting multiple transcript formats.

**Acceptance Criteria**:
1. Auto-detects Leexi format (speaker + timestamp lines) vs plain text
2. Leexi: speaker turns parsed with timestamps, noise turns removed, consecutive same-speaker merged
3. Plain text: paragraphs extracted, optional header/attendance parsed, trailing notes preserved
4. Cleaning stats displayed: raw turns → noise removed → clean turns
5. Duration calculated for Leexi format
6. Works with at least: Leexi, Teams Premium, Plaud AI, and manual notes

#### FR-09: Parsing Summary Display
**Priority**: MUST
**Description**: After parsing both files, a summary is displayed before AI analysis begins.

**Acceptance Criteria**:
1. Report summary shows: meeting number, date, section count, point count, language
2. Transcript summary shows: format detected, turn/paragraph count, duration (if Leexi)
3. If report is a blank template (first report), this is clearly indicated
4. User can proceed to AI analysis or go back to re-upload files

---

### 2.3 AI-Powered Transcript Analysis (F3)

#### FR-10: AI Analysis Execution
**Priority**: MUST
**Description**: The parsed report and cleaned transcript are sent to the Claude API for analysis. The AI produces structured proposals for report updates.

**Acceptance Criteria**:
1. Analysis starts when user clicks "Analyze" after parsing summary
2. Loading state shown with progress message ("Analyzing transcript... ~30-60 seconds")
3. API call uses Claude Sonnet model
4. Input: structured report JSON + cleaned transcript text
5. Output: validated JSON with point_updates, new_points, info_exchange, planning, metadata
6. If API call fails, error message shown with option to retry
7. If output JSON is invalid, one automatic retry before showing error

#### FR-11: Incremental Update Mode
**Priority**: MUST
**Description**: When updating an existing report, the AI compares the transcript against existing points and proposes targeted updates.

**Acceptance Criteria**:
1. Existing points that were discussed get update proposals (new subject lines)
2. Topics not matching existing points become new point proposals
3. Info exchange items are updated (existing kept if relevant, new items added)
4. Planning items are updated (existing kept, new milestones added)
5. Metadata auto-incremented (meeting number + 1, dates from transcript)
6. AI uses the same language as the existing report

#### FR-12: First Report Mode
**Priority**: MUST
**Description**: When creating the first report from a template, the AI generates all content from scratch based on the transcript.

**Acceptance Criteria**:
1. No point_updates (empty — no existing points to update)
2. All significant topics from transcript become new_points
3. Points grouped by section (using template section names)
4. 8-20 meaningful points depending on transcript length
5. Info exchange and planning items extracted from transcript
6. Meeting number set to 1
7. Language matches template language

#### FR-13: Analysis Cost Display
**Priority**: SHOULD
**Description**: After analysis, the token usage and estimated cost are displayed.

**Acceptance Criteria**:
1. Input tokens and output tokens shown
2. Estimated cost in USD shown (based on current API pricing)
3. Displayed in a non-intrusive way (info banner, not modal)

---

### 2.4 Document-Like Preview & Inline Editing (F4)

#### FR-14: Document Preview Rendering
**Priority**: MUST
**Description**: The AI proposal is rendered as an HTML document that visually resembles the final Word output, showing the full report structure.

**Acceptance Criteria**:
1. Document renders with a paper-like appearance (white background, margins, max-width)
2. Report header/metadata shown at the top (project name, meeting number, date, location)
3. Sections displayed in document order with section headings
4. Each point displayed as a row with: number, title, subject content, for_whom, due
5. Info exchange table displayed in document flow
6. Planning section displayed in document flow
7. Scroll through the entire document naturally
8. Renders correctly on screens >= 1024px wide (desktop)

#### FR-15: Content Differentiation
**Priority**: MUST
**Description**: Existing content (from previous meetings) and proposed new content (from AI analysis) are visually differentiated.

**Acceptance Criteria**:
1. Existing (previous meeting) content displayed in normal weight, grey/muted color
2. Proposed new content (point updates) displayed in bold, with a highlight background
3. New points have a distinct indicator (e.g., "NEW" badge or colored left border)
4. For each update, the existing content is visible above/before the proposed addition
5. Color coding is consistent and accessible (not relying solely on color)

#### FR-16: Inline Point Editing
**Priority**: MUST
**Description**: The PM can click on any point to edit its content directly within the document preview.

**Acceptance Criteria**:
1. Click on a point's subject area → inline text editor opens
2. Click on a point's title → inline title editor opens
3. Click on for_whom cell → inline text input
4. Click on due cell → inline text input
5. Edit is saved on blur (clicking outside) or Enter key
6. Escape key cancels the edit
7. Changed content is visually marked (e.g., blue border while editing)

#### FR-17: Inline Metadata Editing
**Priority**: MUST
**Description**: Report metadata is editable in a fixed panel (not inline in the document body).

**Acceptance Criteria**:
1. Metadata panel at the top of the page or in a sidebar
2. Editable fields: meeting number, date, distribution date, next meeting date, next meeting time
3. Meeting number is a numeric input
4. Dates use a date picker or formatted text input (DD/MM/YYYY)
5. Changes immediately reflected in the document preview header

#### FR-18: Info Exchange Table Editing
**Priority**: MUST
**Description**: The info exchange table is editable within the document preview.

**Acceptance Criteria**:
1. Info exchange displayed as a table with columns: From, Status, Content, Due Date
2. Each cell is editable on click
3. New rows can be added via an "Add row" button
4. Rows can be deleted via a delete icon/button
5. Empty rows are ignored during generation

#### FR-19: Planning Table Editing
**Priority**: MUST
**Description**: The planning section is editable within the document preview.

**Acceptance Criteria**:
1. Planning items displayed as a list or single-column table
2. Each item is editable on click
3. New items can be added
4. Items can be deleted
5. New/modified items are visually marked (bold indicator)

#### FR-20: Add/Remove Points
**Priority**: MUST
**Description**: The PM can add new points manually or remove AI-proposed points.

**Acceptance Criteria**:
1. Each proposed new point has a "Remove" button or toggle
2. "Add point" button available per section
3. Manually added points require: title, section, subject content
4. Removed points are excluded from the final report
5. Point numbering auto-adjusts when points are added/removed

#### FR-21: Accept/Reject Updates
**Priority**: MUST
**Description**: Each AI-proposed update to an existing point can be individually accepted or rejected.

**Acceptance Criteria**:
1. Each point update has an accept/reject toggle (default: accepted)
2. Rejected updates are visually dimmed and excluded from generation
3. Accepted updates are included in the final report with bold formatting
4. Bulk accept/reject all is available

---

### 2.5 Quality Analysis Loop (F5)

#### FR-22: Quality Check Execution
**Priority**: MUST
**Description**: An automated quality check runs against the current report state, checking defined criteria.

**Acceptance Criteria**:
1. Quality check runs automatically after AI analysis
2. Quality check re-runs after user edits (on demand via "Re-check quality" button)
3. Quality check re-runs before download attempt
4. Results displayed as a checklist with pass/fail per criterion

#### FR-23: Blocking Criteria (Q1-Q4)
**Priority**: MUST
**Description**: Certain quality criteria must pass before the report can be downloaded.

**Acceptance Criteria**:
1. Q1 — All metadata filled: meeting number, date, distribution date, next meeting all present
2. Q2 — Report number integrity: equals previous + 1, or equals 1 for first report
3. Q3 — Content exists: at least one new point OR one modified point in the report
4. Q4 — Bold formatting: all new/modified content is marked for bold in the output
5. If any Q1-Q4 fails: download button is disabled with explanation of what's missing
6. Failed blocking criteria highlighted in red

#### FR-24: Warning Criteria (Q5-Q10)
**Priority**: SHOULD
**Description**: Additional quality criteria that flag potential issues but don't block download.

**Acceptance Criteria**:
1. Q5 — No duplicate point numbers
2. Q6 — Content language matches report language (detected vs written)
3. Q7 — New point titles are 2-5 words
4. Q8 — Subject content is at least one meaningful sentence per point
5. Q9 — Info exchange items have status and due date
6. Q10 — Report date is plausible (not more than 30 days in the past, not in the future)
7. Warnings displayed with yellow indicator and explanation
8. Download allowed despite warnings (user acknowledges)

#### FR-25: Quality Score Display
**Priority**: SHOULD
**Description**: An overall quality score summarizes the report quality.

**Acceptance Criteria**:
1. Score displayed as percentage (0-100%) or fraction (e.g., 8/10 criteria passed)
2. Breakdown visible: how many blocking passed, how many warnings passed
3. Score updates after user edits and re-check

---

### 2.6 User Feedback & AI Re-Generation (F6)

#### FR-26: Feedback Input
**Priority**: MUST
**Description**: The PM can provide natural-language feedback on the AI proposal to request adjustments.

**Acceptance Criteria**:
1. Text input area available on the review screen (below or beside the document preview)
2. Placeholder text with examples: "Merge points 07.03 and 07.04", "Add more detail about..."
3. "Re-analyze with feedback" button triggers a new AI call
4. Feedback text is sent as additional context to the AI (not replacing the original analysis)
5. Previous proposal remains visible until new proposal is ready

#### FR-27: Feedback Re-Generation
**Priority**: MUST
**Description**: The AI processes the feedback and generates an updated proposal.

**Acceptance Criteria**:
1. AI receives: original report + transcript + current proposal state + user feedback text
2. AI returns updated proposals (same JSON structure)
3. Only affected sections are regenerated (not the entire report)
4. Updated content replaces previous proposal in the preview
5. Loading state shown during re-generation
6. Re-generation can be done multiple times (no limit)
7. Each re-generation shows cost (same as FR-13)

---

### 2.7 Report Generation & Download (F7)

#### FR-28: Report .docx Generation
**Priority**: MUST
**Description**: The final report is generated as a .docx file from the edited proposal, preserving the original template formatting.

**Acceptance Criteria**:
1. Output is a valid .docx file openable in Microsoft Word
2. All template formatting preserved: fonts, colors, header/logo, table styles, cell widths
3. Previous meeting content is un-bolded (demoted from latest)
4. New/updated content for this meeting is in bold
5. New point rows match the table structure of existing points
6. Metadata updated: meeting number, date, distribution date
7. Next meeting info updated if changed
8. Info exchange table reflects the edited state
9. Planning table reflects the edited state

#### FR-29: Filename Auto-Generation
**Priority**: MUST
**Description**: The output filename follows the naming convention of the input file, with incremented meeting number and updated date.

**Acceptance Criteria**:
1. Meeting N-number in filename is updated (e.g., N12 → N13)
2. Date in filename (YYYYMMDD) is updated to the new meeting date
3. Project prefix preserved (e.g., "Penta_MoM-PV")
4. Extension is .docx
5. Example: `Penta_MoM-PV N12 20260204.docx` → `Penta_MoM-PV N13 20260211.docx`

#### FR-30: Download
**Priority**: MUST
**Description**: The PM downloads the generated .docx file.

**Acceptance Criteria**:
1. Download button is prominent and clearly labeled
2. Download is blocked if blocking quality criteria (Q1-Q4) fail (see FR-23)
3. If warnings exist, user sees warning summary but can proceed
4. File downloads to the browser's default download location
5. After download, option to "Start new report" resets the workspace

---

### 2.8 Template Management (F8)

#### FR-31: Template Storage
**Priority**: MUST
**Description**: Report templates are stored server-side and available to all PMs.

**Acceptance Criteria**:
1. Main Immo-Pro template stored in Supabase Storage
2. Template is loaded when PM selects "First report" mode
3. Template can be updated by admin (upload new version)

#### FR-32: Template Selection
**Priority**: COULD
**Description**: Multiple template variants can be stored for different project types or PM preferences.

**Acceptance Criteria**:
1. Template list displayed when PM selects "First report" mode
2. Each template has a name/label (e.g., "Standard", "Compact", "French")
3. PM selects one template before proceeding
4. Default template is pre-selected

---

### 2.9 Usage Tracking (F9)

#### FR-33: Generation Logging
**Priority**: SHOULD
**Description**: Each report generation event is logged for tracking and analytics.

**Acceptance Criteria**:
1. Log entry includes: user email, timestamp, project name (from report), input filenames, mode (update/first)
2. Log entry includes: AI token usage and estimated cost
3. Logs stored in Supabase table (`generation_logs`)
4. Logs are append-only (no modification/deletion by users)

#### FR-34: Admin Usage Dashboard
**Priority**: COULD
**Description**: Admin users can view usage statistics.

**Acceptance Criteria**:
1. Dashboard accessible only to admin users
2. Shows: total reports generated, reports per user, reports per week/month
3. Shows: total AI cost (estimated)
4. Simple table or chart layout

---

## 3. Non-Functional Requirements

#### NFR-01: Performance
**Priority**: MUST

| Metric | Target |
|--------|--------|
| Login page load | < 2 seconds |
| File upload (5MB) | < 5 seconds |
| Report parsing | < 5 seconds |
| AI analysis | < 90 seconds (display progress) |
| Document preview render | < 3 seconds |
| .docx generation | < 10 seconds |

#### NFR-02: Security
**Priority**: MUST

1. API keys (Anthropic) stored server-side only — never exposed to client
2. Uploaded files processed in memory or temp storage — deleted after session ends
3. No permanent storage of .docx/.txt files (client data sensitivity)
4. Supabase Row-Level Security on all tables
5. Session tokens use httpOnly cookies
6. HTTPS enforced on all endpoints

#### NFR-03: Availability
**Priority**: MUST

1. Target uptime: 99% (managed infrastructure: Vercel + Supabase)
2. Graceful error handling — no blank screens on failures
3. Clear error messages with retry options

#### NFR-04: Cost
**Priority**: MUST

1. Infrastructure OPEX: < 50 EUR/month for 5-10 users
2. AI cost per report: < $0.20 (Claude Sonnet pricing)
3. Vercel: Free or Pro tier ($20/month)
4. Supabase: Free tier (sufficient for this scale)

#### NFR-05: Browser Compatibility
**Priority**: MUST

1. Chrome (latest 2 versions) — primary
2. Edge (latest 2 versions)
3. Firefox (latest 2 versions)
4. Safari not required (no Mac users expected)

#### NFR-06: Data Privacy
**Priority**: MUST

1. Uploaded files are processed transiently — not stored after the session
2. AI API calls use Anthropic's standard data handling (no training on user data)
3. Only metadata logged (filenames, timestamps) — not file contents
4. Compliant with internal Immo-Pro data handling policies

#### NFR-07: Maintainability
**Priority**: MUST

1. Codebase documented with inline comments for non-obvious logic
2. Python backend modules maintain the existing clear module separation
3. TypeScript strict mode for frontend
4. All environment variables documented in `.env.example`

#### NFR-08: Scalability
**Priority**: SHOULD

1. Architecture supports scaling to 50 users without redesign
2. Supabase and Vercel scale automatically
3. AI API usage scales linearly with report count

---

## 4. Requirement Traceability Matrix

| Feature | Requirements | Priority Distribution |
|---------|-------------|----------------------|
| F1 — Authentication | FR-01, FR-02, FR-03, FR-04 | 4 MUST |
| F2 — Upload & Parsing | FR-05, FR-06, FR-07, FR-08, FR-09 | 5 MUST |
| F3 — AI Analysis | FR-10, FR-11, FR-12, FR-13 | 3 MUST, 1 SHOULD |
| F4 — Preview & Editing | FR-14 to FR-21 | 8 MUST |
| F5 — Quality Loop | FR-22, FR-23, FR-24, FR-25 | 2 MUST, 2 SHOULD |
| F6 — Feedback Re-Gen | FR-26, FR-27 | 2 MUST |
| F7 — Generation & Download | FR-28, FR-29, FR-30 | 3 MUST |
| F8 — Template Management | FR-31, FR-32 | 1 MUST, 1 COULD |
| F9 — Usage Tracking | FR-33, FR-34 | 1 SHOULD, 1 COULD |
| — Non-Functional | NFR-01 to NFR-08 | 6 MUST, 2 SHOULD |

**Totals**: 34 FR + 8 NFR = 42 requirements
- **MUST**: 28 MUST (launch-critical)
- **SHOULD**: 6 SHOULD (important, can defer)
- **COULD**: 2 COULD (nice-to-have)

---

## 5. Phase Gate Checklist

- [x] All features (F1-F9) mapped to formal requirements
- [x] Every FR has testable acceptance criteria
- [x] Priority assigned to every requirement (MUST/SHOULD/COULD)
- [x] Non-functional requirements defined
- [x] Traceability matrix complete
- [ ] **User validation** — awaiting approval to proceed to Phase 3 (Architecture)
