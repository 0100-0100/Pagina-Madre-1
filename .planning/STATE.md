# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-19)

**Core value:** Users can securely register and authenticate to access the portal.
**Current focus:** v1.3 Async Background Jobs — Cedula Validation

## Current Position

Phase: 15 - Profile Display + Refresh (COMPLETE)
Plan: 2 of 2 complete
Status: Phase 15 complete - HTMX polling and leader refresh button implemented
Last activity: 2026-01-21 — Completed 15-02-PLAN.md (Leader Refresh + RBAC)

Progress: [########..] 5/6 phases (83%)

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

Last session: 2026-01-21
Stopped at: Completed 15-02-PLAN.md (Leader Refresh + RBAC)
Resume file: None
Next: Execute Phase 16 (Referidos Page Updates)

## To Resume Development

Phase 15 complete (2 plans):
- 15-01: HTMX census display with auto-polling on profile page - COMPLETE
- 15-02: Leader-only refresh button with RBAC and 30s cooldown - COMPLETE

Key files created/modified:
- ___/accounts/decorators.py - leader_or_self_required RBAC decorator
- ___/accounts/views.py - refresh_cedula_view with cooldown
- ___/accounts/urls.py - /refrescar-cedula/ routes
- ___/templates/partials/_census_section.html - refresh button with HTMX spinner
- ___/templates/profile.html - showToast event handler

Continue with Phase 16 to update Referidos page with census status display.
