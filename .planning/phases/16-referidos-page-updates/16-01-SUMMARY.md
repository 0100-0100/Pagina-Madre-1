---
phase: 16-referidos-page-updates
plan: 01
subsystem: ui
tags: [htmx, django-templates, javascript, bootstrap, census-display, bulk-actions]

# Dependency graph
requires:
  - phase: 15-profile-display-refresh
    provides: refresh_cedula_view endpoint, HTMX patterns, toast notifications
  - phase: 12-cedulainfo-rbac
    provides: CedulaInfo model with status choices, leader role
provides:
  - Referidos table with census status badges and expandable location details
  - Filter tabs for status categories (All/Pendientes/Encontrados/Errores)
  - Sortable table columns (name, cedula, date, status)
  - Bulk refresh capability for leaders with 30-second cooldown
  - Per-referral refresh button using Phase 15 endpoint
  - Checkbox visibility logic (only for non-final statuses)
affects: [future-leader-dashboards, bulk-operations, reporting-features]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Expandable table rows with detail sections
    - Client-side filtering and sorting without page reload
    - Bulk form submission via HTMX with checkbox selection
    - Empty response partial for toast-only HTMX responses
    - UTC to local time conversion on page load

key-files:
  created:
    - ___/templates/partials/_referral_row.html
    - ___/templates/partials/_empty_response.html
  modified:
    - ___/accounts/views.py
    - ___/accounts/urls.py
    - ___/templates/referidos.html

key-decisions:
  - "Checkbox visibility only for non-final statuses (ACTIVE/CANCELLED excluded from bulk refresh)"
  - "Max 10 referrals per bulk refresh request to prevent queue overload"
  - "Filter tabs use client-side JavaScript instead of server-side filtering for instant response"
  - "Per-referral refresh button reuses refresh_cedula_user endpoint from Phase 15"
  - "Empty response partial for HTMX toast-only responses (no HTML swap needed)"

patterns-established:
  - "Expandable rows: Main row with onclick, detail row toggled via JavaScript"
  - "Bulk actions: Form wraps table, checkboxes controlled by JavaScript, submit button state managed"
  - "Status filtering: Client-side via data attributes for instant response"
  - "Table sorting: Client-side with direction toggle, maintains row/detail pairs"

# Metrics
duration: 3min
completed: 2026-01-21
---

# Phase 16 Plan 01: Referidos Page Updates Summary

**Referidos table displays census status badges with expandable location details, filter tabs, sortable columns, and leader-only bulk refresh with 30-second cooldown**

## Performance

- **Duration:** 3 min
- **Started:** 2026-01-21T13:27:45Z
- **Completed:** 2026-01-21T13:30:31Z
- **Tasks:** 4
- **Files modified:** 5

## Accomplishments

- Leaders can view census status for all referrals in table with color-coded badges
- Clicking any row expands to show full voting location or error details
- Filter tabs instantly filter table by status category without page reload
- Bulk refresh form allows leaders to queue validation for multiple referrals
- Checkboxes only appear for refreshable statuses (excludes ACTIVE/CANCELLED)

## Task Commits

Each task was committed atomically:

1. **Task 1: Update referidos_view and create row partial** - `f17d421` (feat)
2. **Task 2: Create bulk refresh and referral row views with URL routes** - `284cbf6` (feat)
3. **Task 3a: Update referidos.html template structure** - `2a9eac3` (feat)
4. **Task 3b: Add JavaScript interactions to referidos.html** - `a427762` (feat)

## Files Created/Modified

- `___/templates/partials/_referral_row.html` - Single referral row with status badge, expandable details, per-row refresh button
- `___/templates/partials/_empty_response.html` - Empty response for toast-only HTMX swaps
- `___/accounts/views.py` - Updated referidos_view, added bulk_refresh_view and referral_row_view
- `___/accounts/urls.py` - Added bulk-refresh and referral_row URL routes
- `___/templates/referidos.html` - Complete rewrite with filter tabs, sortable table, bulk form, JavaScript interactions

## Decisions Made

**1. Checkbox visibility logic**
- Only show checkboxes for non-final statuses (PENDING, PROCESSING, ERROR, TIMEOUT, BLOCKED, NOT_FOUND)
- ACTIVE and CANCELLED statuses are final and cannot be refreshed
- Prevents leaders from attempting impossible refresh operations

**2. Max 10 bulk refresh limit**
- Limit bulk refresh to first 10 selected referrals
- Prevents queue overload from large selections
- Provides reasonable batch size for typical use cases

**3. Client-side filtering and sorting**
- Implemented via JavaScript instead of server-side pagination
- Instant response with no page reload
- Appropriate for expected dataset size (<100 referrals per leader)

**4. Reuse Phase 15 refresh endpoint**
- Per-referral refresh button uses existing `refresh_cedula_user` URL
- Maintains 30-second cooldown logic already implemented
- HTMX replaces entire row on response (outerHTML swap)

**5. Empty response partial pattern**
- Created `_empty_response.html` for HTMX responses that only trigger toasts
- Cleaner than returning empty string from view
- Template-based approach maintains consistency

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all components integrated smoothly with existing Phase 15 patterns.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 16 complete (1/1 plans). All v1.3 Milestone requirements fulfilled:

**Completed requirements:**
- DISP-03: Referidos table displays status badge for each referral with expandable location details ✓
- DISP-04: Bulk refresh button visible only for leaders, operates on selected checkboxes ✓
- DISP-05: Individual row updates via HTMX after refresh, filter tabs provide status views ✓
- RBAC-06: Bulk refresh restricted to leaders via view-level check ✓

**Key features delivered:**
- Census status visibility for all referrals
- Expandable rows with location or error details
- Filter tabs (All/Pendientes/Encontrados/Errores)
- Sortable columns (name, cedula, date, status)
- Bulk refresh with checkbox selection (max 10)
- Per-referral refresh button (30-second cooldown)
- Empty state with copy-able referral link

**v1.3 Milestone complete** - All 6 phases (11-16) shipped:
- Phase 11: Django-Q2 Foundation ✓
- Phase 12: CedulaInfo Model + RBAC ✓
- Phase 13: Playwright Scraper ✓
- Phase 14: Task Integration + Signals ✓
- Phase 15: Profile Display + Refresh ✓
- Phase 16: Referidos Page Updates ✓

**Next steps:** Ready for production testing or v1.4 planning.

---
*Phase: 16-referidos-page-updates*
*Completed: 2026-01-21*
