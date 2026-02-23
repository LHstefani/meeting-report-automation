# Story 006: Python Backend Setup (Vercel Config, BytesIO Adaptation)

**Epic**: E-2 (Python Backend & File Upload)
**Requirements**: NFR-07
**Dependencies**: Story 001
**Priority**: MUST

## Description
Configure Vercel to run Python serverless functions. Adapt the v1 Python modules to use BytesIO (in-memory) instead of file paths. Create one test endpoint to verify the Python runtime works on Vercel.

## Acceptance Criteria
1. `vercel.json` configures Python 3.11 runtime for `api/*.py` files with 90s maxDuration
2. `requirements.txt` at project root lists: python-docx, anthropic, lxml
3. `report_parser.py` adapted: new function `parse_report_from_bytes(bytesio)` that accepts BytesIO
4. `report_generator.py` adapted: new function `generate_report_from_bytes(source_bytes, updates)` that returns bytes
5. `transcript_cleaner.py` unchanged (already processes text strings)
6. `ai_analyzer.py` adapted: API key from parameter (not hardcoded)
7. Test endpoint `api/health.py` returns `{"status": "ok", "python": "3.11+", "modules": ["python-docx", "anthropic"]}`
8. `vercel dev` or deployment runs the test endpoint successfully
9. All Python modules have no import errors

## Technical Notes
- `parse_report_from_bytes`: wraps existing `parse_report` — `Document(BytesIO(bytes))` works natively
- `generate_report_from_bytes`: replace `shutil.copy2` with BytesIO copy, `doc.save(buffer)`, return `buffer.getvalue()`
- Keep original functions intact (add new ones alongside for backwards compatibility)
- Vercel Python handler pattern: `class handler(BaseHTTPRequestHandler)` with `do_POST`/`do_GET`
- Test locally: `vercel dev` should serve Python functions on `/api/*`

## Files to Create/Modify
- `vercel.json` (add/update Python config)
- `requirements.txt` (at project root)
- `src/report_parser.py` (add BytesIO function)
- `src/report_generator.py` (add BytesIO function)
- `src/ai_analyzer.py` (parameterize API key)
- `api/health.py` (test endpoint)

## Testing
- Deploy to Vercel → `GET /api/health` returns OK with module list
- Or: `vercel dev` locally → same test
- Python import check: `python -c "from src.report_parser import parse_report_from_bytes"`
