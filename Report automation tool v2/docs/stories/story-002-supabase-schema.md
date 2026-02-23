# Story 002: Supabase Schema + RLS + Storage + Seed Data

**Epic**: E-0 (Project Setup)
**Requirements**: NFR-02
**Dependencies**: Story 001
**Priority**: MUST

## Description
Create the Supabase project, define all database tables with RLS policies, create the storage bucket for templates, and seed the initial admin user.

## Acceptance Criteria
1. Supabase project created and linked (URL + keys in `.env.local`)
2. `allowed_emails` table created with columns: id (uuid PK), email (unique, not null), display_name, role (default 'user'), created_at
3. `generation_logs` table created with all columns from ARCHITECTURE.md
4. `templates` table created with columns: id, name, label, storage_path, is_default, created_at
5. RLS enabled on all 3 tables
6. RLS policies match ARCHITECTURE.md specifications
7. `templates` storage bucket created (public read, authenticated write)
8. Initial admin email seeded (leonardo.stefani@lh.engineering, role=admin)
9. Main Immo-Pro template uploaded to storage bucket
10. Supabase client libraries configured (`lib/supabase/client.ts` + `lib/supabase/server.ts`)

## Technical Notes
- Migration SQL: one file with all CREATE TABLE, RLS, and storage commands
- Run via Supabase SQL editor or CLI
- Browser client uses `SUPABASE_ANON_KEY` (public, RLS-protected)
- Server client uses `SUPABASE_SERVICE_ROLE_KEY` (bypasses RLS, server-only)
- Seed template: upload `Template/MAIN TEMPPLATE.docx` to `templates` bucket

## Files to Create
- `lib/supabase/client.ts`
- `lib/supabase/server.ts`
- `lib/types.ts` (TypeScript interfaces for all tables)
- Migration SQL (document in `docs/` or run directly)

## Testing
- Supabase dashboard shows 3 tables with correct columns
- RLS policies visible in Supabase dashboard
- `templates` bucket contains the main template file
- `allowed_emails` has the admin seed row
- Browser client can query `templates` table (public read)
