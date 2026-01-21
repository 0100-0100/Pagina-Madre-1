# Bug Tracker

This file tracks bugs discovered and resolved during development.

---

## Bug #1: TemplateSyntaxError on /referidos/ page

**Milestone:** v1.3 Async Background Jobs
**Date:** 2026-01-21
**Status:** RESOLVED

### Symptom
Page failed to load with error: `'with' received an invalid token: 'and'`

### Location
`___/templates/partials/_referral_row.html:5`

### Root Cause
Django's `{% with %}` template tag only supports simple variable assignments (e.g., `{% with foo=bar %}`). It does not support boolean expressions with operators like `and`, `or`, `!=`, etc.

The code attempted:
```django
{% with can_refresh=is_leader and status != 'ACTIVE' and status != 'CANCELLED_DECEASED' and status != 'CANCELLED_OTHER' %}
```

### Fix
Removed the invalid `{% with %}` block and inlined the boolean condition directly into the two `{% if %}` statements that used `can_refresh`:
```django
{% if is_leader and status != 'ACTIVE' and status != 'CANCELLED_DECEASED' and status != 'CANCELLED_OTHER' %}
```

### Files Changed
- `___/templates/partials/_referral_row.html`

---
