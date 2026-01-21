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

The patch only applies when running Python 3.14+. Later moved to `accounts/apps.py` `ready()` method to avoid import issues in worker processes.

### Files Changed
- `___/accounts/apps.py` (moved monkey-patch here)
- `___/accounts/admin.py` (removed broken Django-Q admin customization - unrelated cleanup)

---

## Bug #3: Django-Q background tasks fail with "Function is not defined"

**Milestone:** v1.3 Async Background Jobs
**Date:** 2026-01-21
**Status:** RESOLVED

### Symptom
Background tasks queued via Django-Q failed with multiple errors:
1. `ValueError: Function accounts.tasks.validate_cedula is not defined`
2. `SynchronousOnlyOperation: You cannot call this from an async context`

### Location
- `django_q/worker.py:101` (function lookup failure)
- `accounts/tasks.py` (async context issue)

### Root Cause
Three interrelated issues:

1. **Python 3.14 multiprocessing `spawn` method**: On macOS, Python 3.14 defaults to `spawn` for multiprocessing. Spawned worker processes start fresh without the parent's `sys.path`, causing `pydoc.locate()` to fail when looking up task functions.

2. **Playwright async event loop**: Playwright's sync API internally runs an asyncio event loop. Django detects this and blocks synchronous database operations with `SynchronousOnlyOperation`.

3. **Import timing**: The Python 3.14 compatibility patch in `settings.py` imported Django modules too early, causing issues in worker process initialization.

### Fix
Three changes:

1. **Use `fork` instead of `spawn`**: Added multiprocessing configuration in `settings.py`:
```python
import multiprocessing
if multiprocessing.get_start_method(allow_none=True) != 'fork':
    try:
        multiprocessing.set_start_method('fork', force=True)
    except RuntimeError:
        pass
```

2. **Allow async-unsafe operations**: Added to `tasks.py`:
```python
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')
```

3. **Moved Python 3.14 patch**: Moved the `BaseContext.__copy__` monkey-patch from `settings.py` to `accounts/apps.py` `ready()` method to ensure proper import timing.

### Files Changed
- `___/___/settings.py` (multiprocessing fork configuration)
- `___/accounts/tasks.py` (DJANGO_ALLOW_ASYNC_UNSAFE)
- `___/accounts/apps.py` (moved Python 3.14 patch here)

---
