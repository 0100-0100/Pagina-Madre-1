---
phase: 14-task-integration-signals
plan: 01
subsystem: api
tags: [django-q2, signals, async-tasks, exponential-backoff, post-save]

# Dependency graph
requires:
  - phase: 11-django-q2-foundation
    provides: Django-Q2 with ORM broker configured
  - phase: 12-cedulainfo-model-rbac
    provides: CedulaInfo model with status choices
  - phase: 13-playwright-scraper
    provides: RegistraduriaScraper class for cedula validation
provides:
  - post_save signal creates CedulaInfo on user registration
  - validate_cedula task with 3-attempt exponential backoff (1/5/15 min)
  - Transaction-safe task queuing via on_commit
  - Status handlers for found/not_found/cancelled/error outcomes
affects: [15-profile-display-refresh, 16-referidos-page-updates]

# Tech tracking
tech-stack:
  added: []  # No new dependencies, uses existing django-q2 and Django signals
  patterns: [transaction.on_commit for signal-triggered async tasks, schedule() for delayed retries]

key-files:
  created:
    - ___/accounts/signals.py
    - ___/accounts/migrations/0007_cedulainfo_retry_count.py
  modified:
    - ___/accounts/models.py
    - ___/accounts/tasks.py
    - ___/accounts/apps.py

key-decisions:
  - "dispatch_uid for signal deduplication"
  - "schedule() with schedule_type='O' for one-time delayed retry"
  - "Status PROCESSING during scrape, not SCRAPING (matches model choices)"

patterns-established:
  - "Signal-to-task pattern: post_save -> CedulaInfo.create -> on_commit -> async_task"
  - "Retry pattern: schedule() with next_run for exponential backoff"
  - "Error handling: Map scraper status codes to CedulaInfo.Status choices"

# Metrics
duration: 8min
completed: 2026-01-20
---

# Phase 14 Plan 01: Task Integration + Signals Summary

**Post-save signal on CustomUser auto-creates CedulaInfo with PENDING status and queues validate_cedula task via transaction.on_commit, with 3-attempt exponential backoff retry (1/5/15 min) using Django-Q2 schedule()**

## Performance

- **Duration:** 8 min
- **Started:** 2026-01-20T20:33:00Z
- **Completed:** 2026-01-20T20:41:00Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- CedulaInfo model now has retry_count field to track validation attempts
- Post-save signal creates CedulaInfo and queues async task on user registration
- validate_cedula task implements exponential backoff retry (60s, 300s, 900s)
- Status handlers correctly map scraper results to CedulaInfo status choices

## Task Commits

Each task was committed atomically:

1. **Task 1: Add retry_count field to CedulaInfo model** - `24e5f53` (feat)
2. **Task 2: Create signal handler and validate_cedula task** - `7247d29` (feat)
3. **Task 3: Register signals in AppConfig and verify integration** - `636ead3` (feat)

## Files Created/Modified

- `___/accounts/models.py` - Added retry_count field (PositiveSmallIntegerField, default=0)
- `___/accounts/migrations/0007_cedulainfo_retry_count.py` - Migration for retry_count
- `___/accounts/signals.py` - NEW: post_save signal with transaction.on_commit
- `___/accounts/tasks.py` - UPDATED: validate_cedula with retry logic and status handlers
- `___/accounts/apps.py` - UPDATED: Import signals in ready()

## Decisions Made

- Used `dispatch_uid='queue_cedula_validation'` to prevent duplicate signal registration
- Used Django-Q2 `schedule()` with `schedule_type='O'` (Once) for delayed retries instead of native retry
- Status during scraping is PROCESSING (matches existing model choices, not adding new SCRAPING status)
- Raw signal parameter check to skip fixture loading

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all verifications passed on first attempt.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Signal wiring complete, users created will automatically queue validation tasks
- Task runs when qcluster worker is active
- Phase 15 (Profile Display + Refresh) can now show CedulaInfo status to users
- Manual refresh endpoint needed in Phase 15 for LEADER role

---
*Phase: 14-task-integration-signals*
*Completed: 2026-01-20*
