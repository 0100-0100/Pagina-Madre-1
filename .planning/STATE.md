# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-19)

**Core value:** Users can securely register and authenticate to access the portal.
**Current focus:** v1.3 Async Background Jobs — Cedula Validation

## Current Position

Phase: 16 - Referidos Page Updates (COMPLETE)
Plan: 1 of 1 complete
Status: v1.3 Milestone COMPLETE - All async background job features shipped
Last activity: 2026-01-21 — Completed 16-01-PLAN.md (Referidos Census Display + Bulk Refresh)

Progress: [##########] 6/6 phases (100%)

## v1.3 Milestone Overview

**Phases:** 11-16 (6 phases total)
**Requirements:** 31 across 6 categories

| Phase | Name | Requirements | Status |
|-------|------|--------------|--------|
| 11 | Django-Q2 Foundation | 4 | Complete |
| 12 | CedulaInfo Model + RBAC | 9 | Complete (2/2 plans) |
| 13 | Playwright Scraper | 7 | Complete (2/2 plans) |
| 14 | Task Integration + Signals | 3 | Complete (1/1 plan) |
| 15 | Profile Display + Refresh | 6 | Complete (2/2 plans) |
| 16 | Referidos Page Updates | 2 | Complete (1/1 plan) |

## Milestones Shipped

- **v1.2 Referrals** (2026-01-19) - Phases 7-10, 5 plans
- **v1.1 UI Polish** (2026-01-19) - Phases 4-6, 4 plans
- **v1.0 MVP** (2026-01-19) - Phases 1-3, 5 plans

See: .planning/MILESTONES.md for full history

## Accumulated Context

### Key Decisions (carry forward)

- Cedula as username pattern established
- Session security with HTTPONLY, SAMESITE
- Custom middleware for global auth
- Bootstrap 5.3.8 via jsDelivr CDN with SRI
- Real-time validation with 1.5s debounce
- Input filtering for form fields
- Three-step migration for unique fields
- Self-referential ForeignKey with SET_NULL
- filter().first() for graceful referral lookup
- Django PasswordChangeView extension
- navigator.clipboard API for copy functionality
- ORM broker with SQLite for task queue (<100 users)
- Single worker (workers=1) for SQLite write safety
- WAL mode via connection_created signal
- timeout=120s, retry=180s for cedula validation tasks
- 9 granular status choices for CedulaInfo lifecycle
- TextField for raw_response (debug storage, not queried)
- Spanish verbose_names for all user-facing fields
- Role enum inside CustomUser class for namespacing (CustomUser.Role.USER)
- CedulaInfoAdmin fully read-only (data from scraping only)
- Role field read-only for non-superusers
- Browser singleton with lazy initialization for Playwright
- Fresh context per scrape with cleanup in finally block
- Headed browser mode when DEBUG=True for visual debugging
- CSS selectors as module constants for easy maintenance
- Class-level rate limiting (5s minimum between requests)
- 2captcha for reCAPTCHA solving (fully automated)
- Wait for networkidle before interacting with page
- Pattern-based response type detection (not_found, cancelled, found)
- dispatch_uid for signal deduplication
- schedule() with schedule_type='O' for one-time delayed retry
- Status PROCESSING during scrape (matches model choices)
- HTMX 2.0.4 with SRI from unpkg CDN for dynamic updates
- Conditional polling via data-polling attribute checked in hx-trigger
- 5-second polling interval for PENDING/PROCESSING states
- Census section as separate card below profile form
- leader_or_self_required decorator for RBAC checks (self-access first, then role)
- 30-second server-side cooldown using fetched_at timestamp
- HX-Trigger JSON header for showToast events
- Status set to PROCESSING before returning to avoid race conditions
- Checkbox visibility only for non-final statuses (excludes ACTIVE/CANCELLED from bulk refresh)
- Max 10 bulk refresh limit to prevent queue overload
- Client-side filtering and sorting for instant response on referidos table
- Empty response partial for HTMX toast-only responses
- Expandable table rows with detail sections for voting location display

### v1.3 Research Insights

- Django-Q2 with ORM broker (SQLite compatible) - IMPLEMENTED
- SQLite WAL mode required to prevent locking - IMPLEMENTED
- Single worker only (Q_CLUSTER.workers = 1) - IMPLEMENTED
- Playwright-stealth for F5 bypass (success not guaranteed)
- transaction.on_commit() for signal-triggered tasks - IMPLEMENTED
- Fresh browser instance per task (no sharing) - IMPLEMENTED via context isolation
- F5 CSPM blocks headless requests - graceful failure implemented

### Pending Todos

- Future: Add semi-automated CAPTCHA fallback (leader manually solves in headed browser mode)

### Blockers/Concerns

(None - reCAPTCHA solved via 2captcha integration)

## Session Continuity

Last session: 2026-01-23
Stopped at: Bug hunting v1.3 - 8 bugs fixed, testing remaining features
Resume file: .planning/phases/bug-hunting-v1.3/.continue-here.md
Next: Continue testing or /gsd:audit-milestone if satisfied

## To Resume Development

**v1.3 Milestone — Bug Hunting Phase** (2026-01-23)

All phases complete. Now in manual verification before archiving:

**Milestone Completion Checklist:**
1. [x] All phases complete (16/16)
2. [x] Manual bug hunting — 8 bugs found and fixed
3. [x] Fix all discovered bugs — all 8 resolved
4. [ ] `/gsd:audit-milestone` — verify requirements
5. [ ] `/gsd:complete-milestone` — archive

**Bug Hunting Status:**
- See BUGTRACKER.md for discovered issues
- Bugs found: 8 (all resolved and verified)
- Key fixes: OOB template wrapper, multiprocessing fork placement

**v1.3 features to verify:**
- [x] Django-Q2 background task queue (Bug #3, #8 fixed)
- [x] Playwright census scraping (working with 2captcha)
- [x] Profile census display with HTMX polling (Bug #5 fixed)
- [x] Leader bulk refresh for referrals (Bug #6, #7 fixed)
- [ ] RBAC controls (needs testing)
- [ ] 30-second cooldown (needs testing)
