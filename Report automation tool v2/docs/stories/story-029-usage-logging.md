# Story 029: Usage Logging + Admin Usage Dashboard

**Epic**: E-8 (Templates & Usage Tracking)
**Requirements**: FR-33, FR-34
**Dependencies**: Story 002, Story 026
**Priority**: SHOULD (FR-33), COULD (FR-34)

## Description
Log each report generation event to the `generation_logs` Supabase table and build an admin dashboard displaying usage statistics.

## Acceptance Criteria
1. After successful report generation (Story 026), a log entry is created in `generation_logs`
2. Log entry includes: user_email, timestamp, project_name (extracted from report metadata), input_report_name, input_transcript_name
3. Log entry includes: mode (update/first), ai_tokens_input, ai_tokens_output, ai_cost_estimate
4. Log entry includes: point_updates_count, new_points_count, quality_score (from last quality check)
5. Logs are append-only (no update/delete by users, RLS enforced)
6. Admin page `/admin/usage` displays usage statistics
7. Dashboard shows: total reports generated (all time), reports this month
8. Dashboard shows: reports per user (table: email, count, last generated)
9. Dashboard shows: total estimated AI cost (sum of ai_cost_estimate)
10. Dashboard shows: reports per week for the last 8 weeks (simple table or bar chart)
11. Admin-only access enforced

## Technical Notes
- Logging: call Supabase insert from the Next.js API route that proxies the generate-report response (not from the Python function directly)
- Create a helper: `lib/logging.ts` with `logGeneration(data)` function
- Admin page: `app/admin/usage/page.tsx`
- API route: `app/api/admin/usage/route.ts` — queries `generation_logs` with aggregation
- For charts: use a simple HTML table first (COULD add a chart library like recharts later)
- Supabase queries: use `.select()` with count, group by, and date filters

## Files to Create/Modify
- `lib/logging.ts` (new helper for generation logging)
- `app/api/admin/usage/route.ts` (new API route for usage stats)
- `app/admin/usage/page.tsx` (new admin page)
- `app/(workspace)/page.tsx` or download handler (add logging call after successful generation)

## Testing
- Generate a report → log entry appears in `generation_logs` table
- Log entry contains all required fields (email, project, tokens, cost, counts)
- Admin dashboard shows correct totals
- Reports per user table is accurate
- Non-admin cannot access /admin/usage
- Multiple generations → log count increases, totals update
