# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-19)

**Core value:** Users can securely register and authenticate to access the portal.
**Current focus:** v1.3 Async Background Jobs — Cedula Validation

## Current Position

Phase: 11 - Django-Q2 Foundation
Plan: Not started
Status: Roadmap created, ready for Phase 11 planning
Last activity: 2026-01-19 — Created v1.3 roadmap

Progress: [..........] 0/6 phases (0%)

## v1.3 Milestone Overview

**Phases:** 11-16 (6 phases total)
**Requirements:** 31 across 6 categories

| Phase | Name | Requirements | Status |
|-------|------|--------------|--------|
| 11 | Django-Q2 Foundation | 4 | Not started |
| 12 | CedulaInfo Model + RBAC | 9 | Not started |
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

### v1.3 Research Insights

- Django-Q2 with ORM broker (SQLite compatible)
- SQLite WAL mode required to prevent locking
- Single worker only (Q_CLUSTER.workers = 1)
- Playwright-stealth for F5 bypass (success not guaranteed)
- transaction.on_commit() for signal-triggered tasks
- Fresh browser instance per task (no sharing)

### Pending Todos

(None)

### Blockers/Concerns

- F5 CSPM bot detection may block scraper (build for graceful failure)

## Session Continuity

Last session: 2026-01-19
Stopped at: Roadmap created for v1.3
Resume file: .planning/ROADMAP.md
Next: `/gsd:plan-phase 11` to plan Django-Q2 Foundation

## To Resume Development

v1.3 roadmap complete with 6 phases:

1. **Phase 11:** Django-Q2 Foundation (INFRA-01 to INFRA-04)
2. **Phase 12:** CedulaInfo Model + RBAC (DATA-*, RBAC-01 to RBAC-03)
3. **Phase 13:** Playwright Scraper (SCRP-01 to SCRP-07)
4. **Phase 14:** Task Integration + Signals (TRIG-01 to TRIG-03)
5. **Phase 15:** Profile Display + Refresh (DISP-01, DISP-02, RBAC-04 to RBAC-07)
6. **Phase 16:** Referidos Page Updates (DISP-03, DISP-04)

Ready to plan Phase 11.
