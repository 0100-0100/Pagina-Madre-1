# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-19)

**Core value:** Users can securely register and authenticate to access the portal.
**Current focus:** v1.3 Async Background Jobs — Cedula Validation

## Current Position

Phase: 12 - CedulaInfo Model + RBAC (COMPLETE)
Plan: 2 of 02 complete
Status: Phase complete - ready for Phase 13
Last activity: 2026-01-20 — Completed 12-02-PLAN.md (Role field + Admin)

Progress: [####......] 2/6 phases (33%)

## v1.3 Milestone Overview

**Phases:** 11-16 (6 phases total)
**Requirements:** 31 across 6 categories

| Phase | Name | Requirements | Status |
|-------|------|--------------|--------|
| 11 | Django-Q2 Foundation | 4 | Complete |
| 12 | CedulaInfo Model + RBAC | 9 | Complete (2/2 plans) |
| 13 | Playwright Scraper | 7 | Not started |
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

### v1.3 Research Insights

- Django-Q2 with ORM broker (SQLite compatible) - IMPLEMENTED
- SQLite WAL mode required to prevent locking - IMPLEMENTED
- Single worker only (Q_CLUSTER.workers = 1) - IMPLEMENTED
- Playwright-stealth for F5 bypass (success not guaranteed)
- transaction.on_commit() for signal-triggered tasks
- Fresh browser instance per task (no sharing)

### Pending Todos

(None)

### Blockers/Concerns

- F5 CSPM bot detection may block scraper (build for graceful failure)

## Session Continuity

Last session: 2026-01-20
Stopped at: Completed 12-02-PLAN.md (Phase 12 complete)
Resume file: .planning/phases/13-playwright-scraper/13-01-PLAN.md
Next: Execute Phase 13 (Playwright Scraper)

## To Resume Development

Phase 12 complete with both plans executed:
- 12-01: CedulaInfo model with 9 status choices, voting location fields - COMPLETE
- 12-02: Role field (USER/LEADER), read-only CedulaInfoAdmin, superadmin role editing - COMPLETE

Continue with Phase 13 (Playwright Scraper) to implement cedula validation scraping.
