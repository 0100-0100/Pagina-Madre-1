# Roadmap: v1.3 Async Background Jobs

**Status:** In Progress
**Phases:** 11-16
**Total Plans:** TBD

## Overview

Add background task processing with web scraping to validate user cedulas against Registraduria's electoral census. Six phases: Django-Q2 foundation with SQLite WAL mode, CedulaInfo model with RBAC role fields, Playwright headless browser scraper, task integration with post_save signals, profile display with refresh buttons, and referidos page census data updates. The system auto-triggers validation on registration and allows manual refresh by leaders.

## Phases

- [x] **Phase 11: Django-Q2 Foundation** - Task queue infrastructure with SQLite-safe configuration ✓
- [x] **Phase 12: CedulaInfo Model + RBAC** - Data model for census data and role field for access control ✓
- [x] **Phase 13: Playwright Scraper** - Headless browser scraping with stealth patches ✓
- [x] **Phase 14: Task Integration + Signals** - Background task wiring with post_save triggers ✓
- [ ] **Phase 15: Profile Display + Refresh** - Census display and leader refresh buttons
- [ ] **Phase 16: Referidos Page Updates** - Census data for referred users

## Phase Details

### Phase 11: Django-Q2 Foundation

**Goal:** Background task queue runs reliably with SQLite database.
**Depends on:** Nothing (foundation phase)
**Requirements:** INFRA-01, INFRA-02, INFRA-03, INFRA-04
**Success Criteria** (what must be TRUE):
  1. Django-Q2 installed and visible in Django admin
  2. qcluster process starts without errors
  3. Simple echo task executes and completes successfully
  4. SQLite database not locked during task execution
**Plans:** 1 plan

Plans:
- [x] 11-01-PLAN.md — Install Django-Q2, configure SQLite WAL mode, verify task execution

---

### Phase 12: CedulaInfo Model + RBAC

**Goal:** Census data can be stored and roles control access.
**Depends on:** Phase 11 (Django-Q2 migrations complete)
**Requirements:** DATA-01, DATA-02, DATA-03, DATA-04, DATA-05, DATA-06, RBAC-01, RBAC-02, RBAC-03
**Success Criteria** (what must be TRUE):
  1. CedulaInfo model exists with all status choices visible in admin
  2. New users automatically have role=USER
  3. Admin can change user role to LEADER
  4. CedulaInfo linked to user visible in admin (read-only)
**Plans:** 2 plans

Plans:
- [x] 12-01-PLAN.md — Create CedulaInfo model with 9 status choices and all fields
- [x] 12-02-PLAN.md — Add role field to CustomUser and configure admin

---

### Phase 13: Playwright Scraper

**Goal:** Scraper retrieves census data from Registraduria for any cedula.
**Depends on:** Phase 12 (CedulaInfo model exists to store results)
**Requirements:** SCRP-01, SCRP-02, SCRP-03, SCRP-04, SCRP-05, SCRP-06, SCRP-07
**Success Criteria** (what must be TRUE):
  1. Playwright installed with Chromium browser binary
  2. Scraper returns voting location for valid active cedula
  3. Scraper returns cancelled status for deceased cedula
  4. Scraper returns not_found for invalid cedula
  5. Scraper handles timeout gracefully without crashing
**Plans:** 2 plans

Plans:
- [x] 13-01-PLAN.md — Install Playwright with Chromium, create browser singleton
- [x] 13-02-PLAN.md — Implement scraper with all response types and rate limiting

---

### Phase 14: Task Integration + Signals

**Goal:** Census lookup auto-triggers on registration and retries on failure.
**Depends on:** Phase 13 (scraper exists)
**Requirements:** TRIG-01, TRIG-02, TRIG-03
**Success Criteria** (what must be TRUE):
  1. New user registration queues background task
  2. Task executes after registration transaction commits
  3. Failed task retries with exponential backoff (max 3 attempts)
**Plans:** 1 plan

Plans:
- [x] 14-01-PLAN.md — Signal handler, validate_cedula task, exponential backoff retry

---

### Phase 15: Profile Display + Refresh

**Goal:** Users see their census data and leaders can refresh for referrals.
**Depends on:** Phase 14 (tasks populate CedulaInfo)
**Requirements:** DISP-01, DISP-02, RBAC-04, RBAC-05, RBAC-07 (RBAC-06 deferred to Phase 16)
**Success Criteria** (what must be TRUE):
  1. User's profile page shows census status (pending, found, error)
  2. User's profile page shows voting location when available
  3. Leader sees refresh button for individual users (self and referrals)
  4. Regular users cannot access refresh endpoints for other users
**Plans:** 2 plans

Plans:
- [ ] 15-01-PLAN.md — HTMX setup, census section partial, profile display with polling
- [ ] 15-02-PLAN.md — Leader refresh button, RBAC decorator, rate limiting

---

### Phase 16: Referidos Page Updates

**Goal:** Leaders see census data for all their referred users with live updates.
**Depends on:** Phase 15 (census display and RBAC complete)
**Requirements:** DISP-03, DISP-04, DISP-05, RBAC-06
**Success Criteria** (what must be TRUE):
  1. Referidos table shows census status column for each user
  2. Bulk refresh button visible only to leaders
  3. Page auto-updates when census data is fetched (HTMX polling)
**Plans:** TBD

Plans:
- [ ] 16-01: Referidos page census columns and bulk refresh

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 11. Django-Q2 Foundation | 1/1 | Complete ✓ | 2026-01-19 |
| 12. CedulaInfo Model + RBAC | 2/2 | Complete ✓ | 2026-01-20 |
| 13. Playwright Scraper | 2/2 | Complete ✓ | 2026-01-20 |
| 14. Task Integration + Signals | 1/1 | Complete ✓ | 2026-01-20 |
| 15. Profile Display + Refresh | 0/2 | Planned | - |
| 16. Referidos Page Updates | 0/TBD | Not started | - |

---
*Created: 2026-01-19*
*Milestone: v1.3 Async Background Jobs*
