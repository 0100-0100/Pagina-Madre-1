# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-19)

**Core value:** Users can securely register and authenticate to access the portal.
**Current focus:** v1.3 Async Background Jobs — Cedula Validation

## Current Position

Phase: 13 - Playwright Scraper (COMPLETE)
Plan: 2 of 02 complete
Status: Phase complete - Ready for Phase 14 (Task Integration + Signals)
Last activity: 2026-01-20 — Completed 13-02-PLAN.md (Scraping Logic Implementation)

Progress: [######....] 3/6 phases (50%)

## v1.3 Milestone Overview

**Phases:** 11-16 (6 phases total)
**Requirements:** 31 across 6 categories

| Phase | Name | Requirements | Status |
|-------|------|--------------|--------|
| 11 | Django-Q2 Foundation | 4 | Complete |
| 12 | CedulaInfo Model + RBAC | 9 | Complete (2/2 plans) |
| 13 | Playwright Scraper | 7 | Complete (2/2 plans) |
| 14 | Task Integration + Signals | 3 | Not started |
| 15 | Profile Display + Refresh | 6 | Not started |
| 16 | Referidos Page Updates | 2 | Not started |

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
- raw_html stored only on error states for debugging

### v1.3 Research Insights

- Django-Q2 with ORM broker (SQLite compatible) - IMPLEMENTED
- SQLite WAL mode required to prevent locking - IMPLEMENTED
- Single worker only (Q_CLUSTER.workers = 1) - IMPLEMENTED
- Playwright-stealth for F5 bypass (success not guaranteed)
- transaction.on_commit() for signal-triggered tasks
- Fresh browser instance per task (no sharing) - IMPLEMENTED via context isolation
- F5 CSPM blocks headless requests - graceful failure implemented

### Pending Todos

(None)

### Blockers/Concerns

- F5 CSPM bot detection blocks scraper (graceful failure implemented, may need playwright-stealth later)

## Session Continuity

Last session: 2026-01-20
Stopped at: Completed 13-02-PLAN.md (Scraping Logic Implementation)
Resume file: None
Next: Execute Phase 14 (Task Integration + Signals)

## To Resume Development

Phase 13 complete:
- 13-01: Playwright 1.57 installed, RegistraduriaScraper class with browser singleton - COMPLETE
- 13-02: Full scraping logic with 7 response types and 5s rate limiting - COMPLETE

Continue with Phase 14 to wire scraper into Django-Q2 background tasks with signals.
