# Story 032: Production Deployment + Final Testing

**Epic**: E-9 (Polish & Production)
**Requirements**: NFR-04, NFR-05
**Dependencies**: All previous stories
**Priority**: MUST

## Description
Deploy the application to Vercel production, configure all environment variables, verify Supabase production setup, run end-to-end testing across supported browsers, and confirm cost targets are met.

## Acceptance Criteria
1. Application deployed to Vercel production (custom domain or Vercel subdomain)
2. All environment variables configured in Vercel dashboard (Anthropic API key, Supabase URL, Supabase keys, JWT secret)
3. Supabase project configured for production: RLS enabled on all tables, storage bucket policies set
4. HTTPS enforced on all endpoints (Vercel default)
5. Python serverless functions deploy and execute correctly on Vercel
6. End-to-end test: login → upload report + transcript → AI analysis → edit → quality check → generate → download
7. End-to-end test: first report mode with template → analysis → edit → generate → download
8. Generated .docx opens correctly in Microsoft Word (Windows)
9. Application works in Chrome (latest), Edge (latest), Firefox (latest)
10. Performance targets met: login < 2s, upload < 5s, parsing < 5s, analysis < 90s, preview < 3s, generation < 10s
11. Infrastructure cost within target: < 50 EUR/month for 5-10 users
12. Seed data: at least one admin email and one template uploaded to production
13. Error monitoring: Vercel's built-in error tracking active (or Sentry if needed)

## Technical Notes
- Vercel deployment: link GitHub repo, configure build settings (Next.js auto-detected)
- Python functions: verify `vercel.json` or `api/` directory structure is correctly recognized
- Environment variables: set via Vercel dashboard → Settings → Environment Variables
- Supabase: create production project (separate from dev), run migration SQL, enable RLS
- Browser testing: manual testing in Chrome, Edge, Firefox — Safari not required (NFR-05)
- Performance: use browser DevTools Network tab to measure load times
- Cost verification: Vercel billing page + Supabase usage page + Anthropic API usage

## Files to Create/Modify
- `vercel.json` (verify/create deployment configuration for Python + Next.js)
- `README.md` (deployment instructions, env var list, setup guide) — only if not existing
- Production Supabase: run schema SQL from Story 002
- No code changes expected — this is a deployment and verification story

## Testing
- Visit production URL → login page loads < 2 seconds
- Login with approved email → workspace loads
- Login with non-approved email → access denied
- Upload .docx + .txt → parsing completes < 5 seconds each
- AI analysis completes < 90 seconds
- Document preview renders < 3 seconds
- Edit points, run quality check → results correct
- Generate and download report → valid .docx, correct formatting
- Test in Chrome, Edge, Firefox → all functional
- Check Vercel billing → within budget
- Check Supabase usage → within free tier
