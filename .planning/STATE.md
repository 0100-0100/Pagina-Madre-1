# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-19)

**Core value:** Users can securely register and authenticate to access the portal.
**Current focus:** v1.3 Async Background Jobs — Cedula Validation

## Current Position

Phase: 12 - CedulaInfo Model + RBAC
Plan: 1 of 02 complete
Status: In progress - 12-01 complete, 12-02 next
Last activity: 2026-01-20 — Completed 12-01-PLAN.md (CedulaInfo Model)

Progress: [##........] 1/6 phases (17%)

## v1.3 Milestone Overview

**Phases:** 11-16 (6 phases total)
**Requirements:** 31 across 6 categories

| Phase | Name | Requirements | Status |
|-------|------|--------------|--------|
| 11 | Django-Q2 Foundation | 4 | Complete |
| 12 | CedulaInfo Model + RBAC | 9 | In progress (1/2 plans) |
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
Stopped at: Completed 12-01-PLAN.md
Resume file: .planning/phases/12-cedulainfo-model-rbac/12-02-PLAN.md
Next: Execute 12-02-PLAN.md (Role field + Admin configuration)

## To Resume Development

Phase 12 in progress with 2 plans in 2 waves:
- 12-01: CedulaInfo model with 9 status choices, voting location fields, cancelled fields, metadata - COMPLETE
- 12-02: Role field on CustomUser (USER/LEADER), read-only CedulaInfoAdmin, role restrictions - NEXT

Continue with 12-02-PLAN.md to complete Phase 12.
