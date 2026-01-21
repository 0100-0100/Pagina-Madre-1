---
phase: 15-profile-display-refresh
plan: 01
subsystem: ui
tags: [htmx, django-templates, polling, census, profile]

# Dependency graph
requires:
  - phase: 14-task-integration-signals
    provides: CedulaInfo model with 9 status choices, post_save signal triggering validation
provides:
  - HTMX 2.0.4 loaded globally in base.html
  - Census section partial with all status displays
  - /censo/ endpoint for HTMX polling
  - Profile page with "Datos Electorales" section
affects: [16-referidos-page-updates]

# Tech tracking
tech-stack:
  added: [htmx@2.0.4, django.contrib.humanize]
  patterns: [HTMX conditional polling via data attributes, partial template includes]

key-files:
  created:
    - ___/templates/partials/_census_section.html
  modified:
    - ___/templates/base.html
    - ___/templates/profile.html
    - ___/accounts/views.py
    - ___/accounts/urls.py
    - ___/___/settings.py

key-decisions:
  - "HTMX 2.0.4 with SRI from unpkg CDN for dynamic updates"
  - "Conditional polling via data-polling attribute checked in hx-trigger"
  - "5-second polling interval for PENDING/PROCESSING states"
  - "Census section as separate card below profile form"

patterns-established:
  - "HTMX partial templates in ___/templates/partials/ directory"
  - "Conditional polling: hx-trigger='every Xs [condition]' pattern"
  - "Status badges with Bootstrap colors matching severity"

# Metrics
duration: 2min
completed: 2026-01-21
---

# Phase 15 Plan 01: Profile Display + Refresh Summary

**HTMX-powered census status display with auto-polling for pending states and voting location details for verified users**

## Performance

- **Duration:** 2 min
- **Started:** 2026-01-21T07:03:00Z
- **Completed:** 2026-01-21T07:05:11Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Added HTMX 2.0.4 globally for dynamic partial updates
- Created census section partial handling all 9 CedulaInfo status states
- Implemented conditional HTMX polling that stops on final states
- Integrated census display into user profile page

## Task Commits

Each task was committed atomically:

1. **Task 1: Add HTMX + humanize and create census section partial** - `a991156` (feat)
2. **Task 2: Create census section view and integrate into profile** - `4c40e43` (feat)

## Files Created/Modified

- `___/templates/base.html` - Added HTMX 2.0.4 script after Bootstrap JS
- `___/___/settings.py` - Added django.contrib.humanize to INSTALLED_APPS
- `___/templates/partials/_census_section.html` - New partial with all 9 status displays
- `___/accounts/views.py` - Added census_section_view and updated profile_view context
- `___/accounts/urls.py` - Added /censo/ route
- `___/templates/profile.html` - Added Datos Electorales card with include

## Decisions Made

- **HTMX from unpkg CDN:** Used unpkg.com with SRI hash for HTMX 2.0.4, consistent with existing CDN strategy
- **Conditional polling via data attribute:** Used `data-polling` attribute with JavaScript condition in hx-trigger rather than server-side headers for simplicity
- **5-second polling interval:** Balanced responsiveness with server load for background task completion
- **Separate card for census data:** Kept census section in its own card below profile form for visual separation

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- HTMX infrastructure now available for Phase 16 (Referidos page updates)
- Polling pattern established for any future real-time updates
- Profile page ready for users to see their cedula validation status

---
*Phase: 15-profile-display-refresh*
*Completed: 2026-01-21*
