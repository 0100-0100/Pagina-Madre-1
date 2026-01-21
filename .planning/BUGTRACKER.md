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

## Bug #2: AttributeError in Django admin pages

**Milestone:** v1.3 Async Background Jobs
**Date:** 2026-01-21
**Status:** RESOLVED

### Symptom
All Django admin model pages failed to load with error: `'super' object has no attribute 'dicts' and no __dict__ for setting new attributes`

### Location
`django/template/context.py:39` (Django 4.2 core code)

### Root Cause
Django 4.2's `BaseContext.__copy__` method uses `copy(super())` pattern:
```python
def __copy__(self):
    duplicate = copy(super())  # ← Fails in Python 3.14
    duplicate.dicts = self.dicts[:]
    return duplicate
```

Python 3.14 changed how `super()` objects work - they no longer support being copied via `copy()` because they don't have `__dict__`. This is a **Django 4.2 incompatibility with Python 3.14**.

### Fix
Added a monkey-patch in `settings.py` that replaces `BaseContext.__copy__` with a Python 3.14-compatible implementation:
```python
def _patched_base_context_copy(self):
    duplicate = object.__new__(type(self))
    duplicate.__dict__.update(self.__dict__)
    duplicate.dicts = self.dicts[:]
    return duplicate
```

The patch only applies when running Python 3.14+.

### Files Changed
- `___/___/settings.py` (added monkey-patch)
- `___/accounts/admin.py` (removed broken Django-Q admin customization - unrelated cleanup)

---
