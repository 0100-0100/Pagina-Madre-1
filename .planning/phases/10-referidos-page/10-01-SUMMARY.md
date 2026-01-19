---
phase: 10-referidos-page
plan: 01
status: complete

subsystem: referrals
tags: [django, referrals, ui]

dependency_graph:
  requires: [07-referral-model]
  provides: [referidos-page, referral-list-view]
  affects: []

tech_stack:
  added: []
  patterns: [reverse-fk-query, empty-state-pattern]

key_files:
  created:
    - ___/templates/referidos.html
  modified:
    - ___/accounts/views.py
    - ___/accounts/urls.py

decisions:
  - context: "Empty state display"
    choice: "Centered card with icon and CTA"
    reason: "Consistent with existing UI patterns, guides users to share referral link"

metrics:
  duration: "5 minutes"
  completed: "2026-01-19"
---

# Phase 10 Plan 01: Referidos Page Summary

**One-liner:** Bootstrap table displaying referred users with empty state fallback via reverse ForeignKey query

## What Was Built

### Task 1: referidos_view and URL routing
- Added `referidos_view` function with `@login_required` decorator
- Query: `request.user.referrals.all().order_by('-date_joined')`
- Updated `/referidos/` route from placeholder to actual view

### Task 2: referidos.html template
- Table with columns: Nombre, Cedula, Telefono, Fecha de registro
- Responsive table wrapped in `table-responsive` div
- Empty state with bi-people icon, message, and "Ir al inicio" button
- Navbar shows Referidos link as active

## Technical Details

**View pattern:**
```python
@login_required
def referidos_view(request):
    referrals = request.user.referrals.all().order_by('-date_joined')
    return render(request, 'referidos.html', {'referrals': referrals})
```

**Template structure:**
- Uses `{% if referrals %}` to conditionally show table or empty state
- Table classes: `table table-striped table-hover`
- Date format: `date_joined|date:"d/m/Y"`

## Commits

| Hash | Type | Description |
|------|------|-------------|
| 68eb8e5 | feat | Add referidos_view and URL routing |
| edf9b1f | feat | Create referidos.html with table and empty state |

## Requirements Satisfied

- **REFR-01:** Table displays Nombre, Cedula, Telefono, Fecha de registro columns
- **REFR-02:** Empty state shows friendly message when user has no referrals

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

1. `/referidos/` redirects anonymous users to login (302)
2. Django check passes with no issues
3. Template has 84 lines (exceeds 40 minimum)
4. All required patterns present in code

## Next Phase Readiness

Phase 10 complete. All v1.2 requirements implemented:
- Phase 7: Referral model and registration capture
- Phase 8: Home page referral UI with progress and copy link
- Phase 9: Profile page with editable fields and password change
- Phase 10: Referidos page with referral table

v1.2 Referrals milestone is ready for final review.
