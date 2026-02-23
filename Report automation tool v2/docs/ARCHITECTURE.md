# Architecture — Immo-Pro Report Automation Tool v2

**Document**: Phase 3 — Architecture
**Author**: CTO Agent (Architect role)
**Date**: 2026-02-23
**Status**: DRAFT — awaiting user validation
**Dependencies**: `docs/product-brief.md` (Phase 1), `docs/PRD.md` (Phase 2)

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         VERCEL                                  │
│                                                                 │
│  ┌──────────────────────┐    ┌────────────────────────────┐    │
│  │   Next.js Frontend   │    │   Python Serverless Fns    │    │
│  │                      │    │                            │    │
│  │  /login              │    │  /api/parse-report         │    │
│  │  / (workspace)       │───>│  /api/parse-transcript     │    │
│  │  /admin              │    │  /api/analyze              │    │
│  │                      │    │  /api/analyze-feedback     │    │
│  │  Middleware (JWT)     │    │  /api/generate-report      │    │
│  │                      │    │  /api/quality-check        │    │
│  └──────────┬───────────┘    └─────────────┬──────────────┘    │
│             │                              │                    │
│  ┌──────────┴───────────┐                  │                    │
│  │  Next.js API Routes  │                  │                    │
│  │  /api/auth/*         │                  │                    │
│  │  /api/admin/*        │                  │                    │
│  │  /api/templates      │                  │                    │
│  └──────────┬───────────┘                  │                    │
└─────────────┼──────────────────────────────┼────────────────────┘
              │                              │
              ▼                              ▼
┌──────────────────────┐        ┌──────────────────────┐
│      SUPABASE        │        │    ANTHROPIC API      │
│                      │        │                       │
│  PostgreSQL:         │        │  Claude Sonnet        │
│  - allowed_emails    │        │  ~$0.05-0.15/report   │
│  - generation_logs   │        │                       │
│  - templates         │        └──────────────────────┘
│                      │
│  Storage:            │
│  - templates bucket  │
│                      │
└──────────────────────┘
```

### Key Architectural Decisions

1. **Single-platform deployment**: Both Next.js and Python functions run on Vercel in the same repo. No cross-origin issues, no separate infrastructure.
2. **Python for document processing**: The v1 Python code (parser, cleaner, AI analyzer, generator) is reused as Vercel serverless functions. File I/O adapted to use `BytesIO` (in-memory).
3. **Next.js API routes for auth/admin**: Authentication and admin operations use Node.js API routes (JWT, Supabase queries). Document processing uses Python functions.
4. **Transient file handling**: Uploaded .docx/.txt files are never stored permanently. They are processed in-memory within the Python function and discarded. Only metadata is logged.

---

## 2. Frontend Architecture

### Pages & Routing

```
app/
├── login/
│   └── page.tsx                # FR-01: Email login
├── (workspace)/
│   ├── layout.tsx              # Authenticated layout (header, sidebar)
│   └── page.tsx                # Main workspace (upload → edit → download)
├── admin/
│   ├── layout.tsx              # Admin-only layout
│   ├── page.tsx                # Admin dashboard
│   ├── emails/
│   │   └── page.tsx            # FR-03: Email allowlist management
│   ├── templates/
│   │   └── page.tsx            # FR-31: Template management
│   └── usage/
│       └── page.tsx            # FR-34: Usage statistics
├── api/
│   ├── auth/
│   │   ├── login/route.ts      # POST: validate email, create JWT
│   │   ├── logout/route.ts     # POST: clear session cookie
│   │   └── check/route.ts      # GET: verify current session
│   ├── admin/
│   │   ├── emails/route.ts     # GET/POST/DELETE: manage allowlist
│   │   └── usage/route.ts      # GET: usage statistics
│   └── templates/route.ts      # GET: list templates
├── middleware.ts                # JWT verification, route protection
└── layout.tsx                  # Root layout
```

### Python API Functions (Vercel)

```
api/
├── parse-report.py             # POST: upload .docx → parsed JSON
├── parse-transcript.py         # POST: upload .txt → cleaned text + stats
├── analyze.py                  # POST: parsed report + transcript → AI proposals
├── analyze-feedback.py         # POST: current state + feedback → updated proposals
├── generate-report.py          # POST: source .docx + updates → .docx binary
└── quality-check.py            # POST: current state → quality results
```

### State Management (zustand)

The main workspace manages a complex editing state:

```typescript
interface ReportStore {
  // Step tracking
  step: 'upload' | 'parsing' | 'review' | 'download';

  // Parsed data (from Python backend)
  parsedReport: ParsedReport | null;
  cleanedTranscript: CleanedTranscript | null;

  // AI proposals (from Python backend)
  proposals: AIProposals | null;

  // User edits (client-side)
  metadata: ReportMetadata;
  pointUpdates: PointUpdate[];       // with accept/reject state
  newPoints: NewPoint[];             // with include/exclude state
  infoExchange: InfoExchangeItem[];
  planning: PlanningItem[];

  // Quality
  qualityResults: QualityResult | null;

  // Actions
  setStep: (step: Step) => void;
  updateMetadata: (field: string, value: string) => void;
  togglePointUpdate: (index: number) => void;
  editPointContent: (index: number, field: string, value: string) => void;
  addNewPoint: (sectionName: string) => void;
  removeNewPoint: (index: number) => void;
  // ... etc.
  reset: () => void;
}
```

### Document Preview Component Architecture

```
<WorkspacePage>
  ├── <StepIndicator />          # Upload → Review → Download
  │
  ├── [step=upload]
  │   ├── <FileUploader />       # Drag-and-drop .docx + .txt
  │   ├── <FirstReportToggle />  # Template selector
  │   └── <ParsingSummary />     # After upload: section count, etc.
  │
  ├── [step=review]
  │   ├── <MetadataPanel />      # Fixed top: meeting #, dates
  │   ├── <DocumentPreview>      # Main scrollable area
  │   │   ├── <ReportHeader />   # Project name, meeting info
  │   │   ├── <AttendanceTable />
  │   │   ├── <SectionBlock>     # Repeated per section
  │   │   │   ├── <SectionHeading />
  │   │   │   ├── <PointRow>     # Repeated per point
  │   │   │   │   ├── <PointNumber />
  │   │   │   │   ├── <PointTitle />     # Click to edit
  │   │   │   │   ├── <PointContent>     # Existing (grey) + New (bold/highlight)
  │   │   │   │   │   ├── <ExistingContent />  # Read-only, muted
  │   │   │   │   │   └── <ProposedContent />  # Editable, highlighted
  │   │   │   │   ├── <ForWhomCell />    # Click to edit
  │   │   │   │   └── <DueCell />        # Click to edit
  │   │   │   └── <AddPointButton />
  │   │   ├── <InfoExchangeTable />      # Editable rows
  │   │   └── <PlanningTable />          # Editable rows
  │   ├── <QualityPanel />       # Quality check results
  │   ├── <FeedbackInput />      # FR-26: natural language feedback
  │   └── <ActionBar />          # Re-check / Re-analyze / Generate
  │
  └── [step=download]
      ├── <DownloadButton />
      └── <GenerationSummary />
```

---

## 3. Backend Architecture (Python)

### Module Structure

The v1 Python modules are adapted for serverless execution:

```
Report automation tool v2/
└── src/
    ├── __init__.py
    ├── report_parser.py         # Adapted: accepts BytesIO input
    ├── transcript_cleaner.py    # Unchanged: processes text strings
    ├── ai_analyzer.py           # Adapted: API key from env var
    ├── report_generator.py      # Adapted: BytesIO input/output
    └── quality_checker.py       # NEW: implements Q1-Q10 checks
```

### Vercel Python Function Pattern

Each API endpoint follows this pattern:

```python
# api/parse-report.py
from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        # Process the uploaded .docx in memory
        from src.report_parser import parse_report_from_bytes
        result = parse_report_from_bytes(BytesIO(body))

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
```

### Key Adaptation: In-Memory File Processing

The v1 code uses file paths. For Vercel serverless (no disk), all file operations are adapted to use `BytesIO`:

| v1 (file-based) | v2 (memory-based) |
|------------------|--------------------|
| `Document(docx_path)` | `Document(BytesIO(bytes))` |
| `shutil.copy2(src, dest)` | `BytesIO(src_bytes)` |
| `doc.save(output_path)` | `doc.save(output_buffer); output_buffer.getvalue()` |
| `Path(file).read_text()` | Direct string from request body |

`python-docx` natively supports `BytesIO` for both reading and writing. The adaptation is minimal.

---

## 4. Data Model (Supabase)

### Tables

#### `allowed_emails`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, default gen | |
| email | text | UNIQUE, NOT NULL | Case-insensitive (stored lowercase) |
| display_name | text | | PM's name (for logs/display) |
| role | text | NOT NULL, default 'user' | 'admin' or 'user' |
| created_at | timestamptz | default now() | |

#### `generation_logs`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, default gen | |
| user_email | text | NOT NULL, FK → allowed_emails.email | Who generated |
| project_name | text | | Extracted from report metadata |
| input_report_name | text | | Original .docx filename |
| input_transcript_name | text | | Original .txt filename |
| mode | text | NOT NULL | 'update' or 'first_report' |
| ai_tokens_input | integer | | Claude API input tokens |
| ai_tokens_output | integer | | Claude API output tokens |
| ai_cost_estimate | numeric(6,4) | | Estimated cost in USD |
| point_updates_count | integer | | Number of point updates |
| new_points_count | integer | | Number of new points |
| quality_score | integer | | Quality check score (0-100) |
| created_at | timestamptz | default now() | |

#### `templates`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, default gen | |
| name | text | NOT NULL | Internal name |
| label | text | NOT NULL | Display label ("Standard", "Compact") |
| storage_path | text | NOT NULL | Path in Supabase Storage |
| is_default | boolean | default false | Pre-selected in template picker |
| created_at | timestamptz | default now() | |

### Row-Level Security (RLS)

| Table | Policy | Description |
|-------|--------|-------------|
| `allowed_emails` | SELECT: authenticated users can read own row | Self-lookup for role check |
| `allowed_emails` | ALL: admin role only | Full CRUD for admins |
| `generation_logs` | INSERT: authenticated users | Any PM can log their generation |
| `generation_logs` | SELECT: own logs OR admin | PMs see own; admins see all |
| `templates` | SELECT: all authenticated | Any PM can list templates |
| `templates` | INSERT/UPDATE/DELETE: admin only | Only admins manage templates |

### Storage Bucket

| Bucket | Access | Content |
|--------|--------|---------|
| `templates` | Public read, admin write | .docx template files |

---

## 5. Authentication Flow

```
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PM      │    │  /login page │    │  /api/auth/  │    │  Supabase    │
│  Browser │    │              │    │  login       │    │  allowed_    │
│          │    │              │    │              │    │  emails      │
└────┬─────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
     │                 │                   │                   │
     │  Enter email    │                   │                   │
     ├────────────────>│                   │                   │
     │                 │  POST /api/auth/  │                   │
     │                 │  login {email}    │                   │
     │                 ├──────────────────>│                   │
     │                 │                   │  SELECT * WHERE   │
     │                 │                   │  email = lower()  │
     │                 │                   ├──────────────────>│
     │                 │                   │                   │
     │                 │                   │  Row found        │
     │                 │                   │<──────────────────┤
     │                 │                   │                   │
     │                 │  Set-Cookie:      │                   │
     │                 │  session=JWT      │                   │
     │                 │  (httpOnly)       │                   │
     │                 │<──────────────────┤                   │
     │  Redirect to /  │                   │                   │
     │<────────────────┤                   │                   │
```

**JWT Payload**:
```json
{
  "email": "pm@immo-pro.be",
  "name": "Joelle Stevens",
  "role": "user",
  "exp": 1740000000
}
```

**Middleware**: `middleware.ts` checks the JWT on every request to `/(workspace)` and `/admin` routes. Expired or missing JWT → redirect to `/login`. Admin routes additionally check `role === 'admin'`.

---

## 6. API Contract

### Python Endpoints (Document Processing)

#### `POST /api/parse-report`
- **Input**: Binary .docx file (multipart/form-data)
- **Output**: `{ metadata, attendance, info_exchange, planning, sections[], language, next_meeting }`
- **Timeout**: 5 seconds

#### `POST /api/parse-transcript`
- **Input**: Plain text body (.txt content)
- **Output**: `{ turns[], speakers, duration_seconds, format, stats }`
- **Timeout**: 5 seconds

#### `POST /api/analyze`
- **Input**: `{ parsed_report: {}, cleaned_text: string, api_key: string }`
- **Output**: `{ meeting_number, date, point_updates[], new_points[], info_exchange[], planning[], usage }`
- **Timeout**: 90 seconds
- **Note**: API key passed from server-side env var, not from client

#### `POST /api/analyze-feedback`
- **Input**: `{ parsed_report: {}, cleaned_text: string, current_proposals: {}, feedback: string, api_key: string }`
- **Output**: Same as `/api/analyze`
- **Timeout**: 90 seconds

#### `POST /api/generate-report`
- **Input**: Multipart — source .docx binary + JSON updates
- **Output**: Binary .docx file
- **Timeout**: 10 seconds

#### `POST /api/quality-check`
- **Input**: `{ metadata: {}, point_updates: [], new_points: [], info_exchange: [], planning: [], previous_meeting_number: int, mode: string }`
- **Output**: `{ score: int, blocking: [{id, passed, message}], warnings: [{id, passed, message}] }`
- **Timeout**: 2 seconds

### Node.js Endpoints (Auth & Admin)

#### `POST /api/auth/login`
- **Input**: `{ email: string }`
- **Output**: `{ success: true, user: { email, name, role } }` + Set-Cookie
- **Error**: `{ success: false, message: "Access denied..." }`

#### `POST /api/auth/logout`
- **Output**: `{ success: true }` + Clear-Cookie

#### `GET /api/auth/check`
- **Output**: `{ authenticated: true, user: { email, name, role } }` or `{ authenticated: false }`

#### `GET /api/admin/emails`
- **Auth**: Admin only
- **Output**: `{ emails: [{ id, email, display_name, role, created_at }] }`

#### `POST /api/admin/emails`
- **Auth**: Admin only
- **Input**: `{ email: string, display_name: string, role: string }`
- **Output**: `{ success: true, id: string }`

#### `DELETE /api/admin/emails/:id`
- **Auth**: Admin only
- **Output**: `{ success: true }`

#### `GET /api/admin/usage`
- **Auth**: Admin only
- **Output**: `{ total_reports, reports_by_user: [], reports_by_month: [], total_ai_cost }`

#### `GET /api/templates`
- **Auth**: Any authenticated user
- **Output**: `{ templates: [{ id, name, label, is_default }] }`

---

## 7. Security Architecture

| Concern | Mitigation |
|---------|-----------|
| API key exposure | Anthropic API key stored in Vercel env vars; accessed only by Python functions server-side |
| Session hijacking | JWT in httpOnly, Secure, SameSite=Strict cookie; 24h expiry |
| Unauthorized access | Middleware verifies JWT on all protected routes; admin routes check role |
| Data persistence | Uploaded files processed in-memory only; never written to disk or storage |
| XSS | React auto-escapes output; Content-Security-Policy headers |
| CSRF | SameSite=Strict cookie; API routes verify Origin header |
| SQL injection | Supabase client uses parameterized queries |

---

## 8. Deployment Architecture

```
GitHub Repo (private)
    │
    ├── Push to master
    │
    ▼
Vercel (auto-deploy)
    │
    ├── Build: Next.js frontend → static + serverless
    ├── Bundle: Python functions → serverless
    │
    ├── Domain: report.immo-pro.be (or Vercel subdomain)
    │
    ├── Env Vars:
    │   ├── ANTHROPIC_API_KEY
    │   ├── SUPABASE_URL
    │   ├── SUPABASE_ANON_KEY
    │   ├── SUPABASE_SERVICE_ROLE_KEY (server-side only)
    │   ├── JWT_SECRET
    │   └── ADMIN_EMAIL (initial admin)
    │
    └── Runtime:
        ├── Node.js 20 (Next.js + API routes)
        └── Python 3.11 (document processing functions)
```

### Environment Variables

| Variable | Used By | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Python functions | Claude API access |
| `SUPABASE_URL` | Node.js + Python | Supabase project URL |
| `SUPABASE_ANON_KEY` | Client-side | Public Supabase key (RLS-protected) |
| `SUPABASE_SERVICE_ROLE_KEY` | Server-side only | Bypass RLS for admin operations |
| `JWT_SECRET` | Node.js middleware | Sign/verify session tokens |
| `ADMIN_EMAIL` | Seed script | Initial admin user email |

---

## 9. Folder Structure

```
report-automation-v2/
├── app/                           # Next.js App Router
│   ├── login/page.tsx
│   ├── (workspace)/
│   │   ├── layout.tsx
│   │   └── page.tsx               # Main workspace
│   ├── admin/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── emails/page.tsx
│   │   ├── templates/page.tsx
│   │   └── usage/page.tsx
│   ├── api/
│   │   ├── auth/login/route.ts
│   │   ├── auth/logout/route.ts
│   │   ├── auth/check/route.ts
│   │   ├── admin/emails/route.ts
│   │   ├── admin/usage/route.ts
│   │   └── templates/route.ts
│   ├── middleware.ts
│   └── layout.tsx
├── api/                           # Vercel Python serverless functions
│   ├── parse-report.py
│   ├── parse-transcript.py
│   ├── analyze.py
│   ├── analyze-feedback.py
│   ├── generate-report.py
│   └── quality-check.py
├── src/                           # Shared Python modules (imported by api/)
│   ├── __init__.py
│   ├── report_parser.py
│   ├── transcript_cleaner.py
│   ├── ai_analyzer.py
│   ├── report_generator.py
│   └── quality_checker.py
├── components/                    # React components
│   ├── ui/                        # shadcn/ui components
│   ├── document-preview/
│   │   ├── document-preview.tsx
│   │   ├── section-block.tsx
│   │   ├── point-row.tsx
│   │   ├── point-content.tsx
│   │   ├── info-exchange-table.tsx
│   │   ├── planning-table.tsx
│   │   └── metadata-panel.tsx
│   ├── file-uploader.tsx
│   ├── quality-panel.tsx
│   ├── feedback-input.tsx
│   ├── step-indicator.tsx
│   └── admin/
│       ├── email-list.tsx
│       ├── usage-chart.tsx
│       └── template-list.tsx
├── lib/                           # Utilities
│   ├── supabase/
│   │   ├── client.ts              # Browser Supabase client
│   │   └── server.ts              # Server Supabase client
│   ├── auth.ts                    # JWT helpers
│   ├── types.ts                   # TypeScript interfaces
│   └── store.ts                   # zustand store definition
├── public/
│   └── logo.png                   # Immo-Pro logo
├── docs/                          # BMAD documentation
├── requirements.txt               # Python dependencies
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
├── vercel.json                    # Python function config
└── .env.example
```

---

## 10. Fallback Plan

If Vercel Python Serverless proves problematic (package size, cold starts, timeout issues):

**Fallback: Vercel (Next.js) + Railway (Python API)**
- Move Python functions to a FastAPI app on Railway ($5/month)
- Add CORS configuration for Vercel → Railway communication
- File uploads route through Next.js API routes (proxy to Railway)
- All other architecture remains unchanged

This fallback requires ~2 hours of restructuring and is fully documented in `docs/tech-stack.md`.

---

## 11. Phase Gate Checklist

- [x] System overview diagram
- [x] Frontend architecture (pages, components, state)
- [x] Backend architecture (Python modules, API pattern)
- [x] Data model (3 tables, RLS policies, storage)
- [x] Authentication flow
- [x] API contract (all endpoints documented)
- [x] Security architecture
- [x] Deployment architecture (env vars, CI/CD)
- [x] Folder structure
- [x] Fallback plan documented
- [x] All tech decisions justified in tech-stack.md
- [ ] **User validation** — awaiting approval to proceed to Phase 4 (Stories)
