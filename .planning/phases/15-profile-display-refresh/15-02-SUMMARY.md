---
phase: 15-profile-display-refresh
plan: 02
subsystem: auth
tags: [rbac, htmx, django-decorators, rate-limiting, async-task]

# Dependency graph
requires:
  - phase: 15-01
    provides: HTMX infrastructure, census section partial, toast container
  - phase: 14
    provides: validate_cedula async task, signal-based task triggering
  - phase: 12
    provides: CedulaInfo model with status field, CustomUser.Role enum
provides:
  - leader_or_self_required RBAC decorator
  - refresh_cedula_view with 30-second server-side cooldown
  - Leader-only refresh button with HTMX integration
  - HX-Trigger toast notifications for user feedback
affects: [16-referidos-update, future-leader-features]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - RBAC decorator pattern for view protection
    - HX-Trigger header for HTMX toast events
    - Server-side rate limiting via model timestamp

key-files:
  created:
    - ___/accounts/decorators.py
  modified:
    - ___/accounts/views.py
    - ___/accounts/urls.py
    - ___/templates/partials/_census_section.html
    - ___/templates/profile.html

key-decisions:
  - "leader_or_self_required decorator checks user_id=None or self or referred_by"
  - "30-second cooldown using fetched_at timestamp"
  - "Status set to PROCESSING before returning to avoid race condition"
  - "HX-Trigger JSON header for showToast events"

patterns-established:
  - "RBAC decorator: checks self-access first, then role-based referral access"
  - "Rate limiting: compare timestamp + timedelta against timezone.now()"
  - "HTMX toast: document.body.addEventListener('showToast', handler)"

# Metrics
duration: 8min
completed: 2026-01-21
---

# Phase 15 Plan 02: Leader Refresh + RBAC Summary

**RBAC-protected refresh button for leaders with 30-second cooldown and HTMX toast feedback**

## Performance

- **Duration:** 8 min
- **Started:** 2026-01-21T07:05:00Z
- **Completed:** 2026-01-21T07:13:00Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Created leader_or_self_required decorator enforcing RBAC for cedula refresh
- Added refresh_cedula_view with 30-second server-side rate limiting
- Integrated refresh button visible only to leaders using conditional template rendering
- Implemented HTMX toast notifications via HX-Trigger header

## Task Commits

Each task was committed atomically:

1. **Task 1: Create RBAC decorator and refresh view** - `a2e657d` (feat)
2. **Task 2: Add refresh button to census section with HTMX + toast handler** - `675e30c` (feat)
3. **Task 3: Test RBAC enforcement end-to-end** - (verification only, no code changes)

## Files Created/Modified

- `___/accounts/decorators.py` - RBAC decorator for leader/self permission checks
- `___/accounts/views.py` - refresh_cedula_view with cooldown and async task queueing
- `___/accounts/urls.py` - Routes for /refrescar-cedula/ and /refrescar-cedula/<user_id>/
- `___/templates/partials/_census_section.html` - Refresh button with HTMX and spinner
- `___/templates/profile.html` - showToast event handler for HX-Trigger toasts

## Decisions Made

1. **RBAC decorator placement:** Applied after login_required to ensure user is authenticated before RBAC check
2. **Cooldown implementation:** Using fetched_at timestamp + timedelta(seconds=30) rather than separate cooldown field
3. **Status update timing:** Set status to PROCESSING before returning response to avoid race condition where multiple requests could queue tasks
4. **Toast event format:** JSON object with message and type keys for flexible styling

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all components integrated smoothly with existing HTMX infrastructure from 15-01.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Leader refresh functionality complete for profile page
- Phase 16 can add similar refresh buttons to referidos page
- RBAC decorator reusable for other leader-only views

---
*Phase: 15-profile-display-refresh*
*Completed: 2026-01-21*
