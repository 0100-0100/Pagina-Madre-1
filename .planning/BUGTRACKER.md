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

## Bug #4: Cedula validation task not queued when registering from remote client

**Milestone:** v1.3 Async Background Jobs
**Date:** 2026-01-21
**Status:** RESOLVED

### Symptom
When registering via iPhone over WiFi (connecting to `0.0.0.0:8000`), the cedula validation background task was never queued. User's profile showed "Verificando Cedula" status indefinitely. Worked correctly when accessing from local machine via `127.0.0.1:8000`.

### Root Cause
The `_queue_validation_task` function had no exception handling. Any failure in `async_task()` was silently swallowed, preventing task queuing without any error visibility.

### Fix
Added comprehensive error handling and logging to `_queue_validation_task`:
```python
def _queue_validation_task(user_id):
    logger.info("on_commit callback fired for user_id=%s", user_id)
    try:
        task_id = async_task(...)
        logger.info("Queued task %s for user_id=%s", task_id, user_id)
    except Exception as e:
        logger.error("Failed to queue for user_id=%s: %s", user_id, e, exc_info=True)
```

### Files Changed
- `___/accounts/signals.py` (added error handling and logging)

---

## Bug #5: UI shows perpetual loading state when task fails to queue

**Milestone:** v1.3 Async Background Jobs
**Date:** 2026-01-21
**Status:** RESOLVED

### Symptom
If a cedula validation task fails to queue (Bug #4) or the worker isn't running, the UI displays "Verificando Cédula" or "Actualizando información" indefinitely. This persists even after logging out and back in, with no way for the user to recover.

### Root Cause
No timeout or stale-state detection for PENDING/PROCESSING statuses. Once stuck, the UI continues polling forever without any recovery mechanism.

### Fix
Added stale status detection to CedulaInfo model and automatic reset in views:

1. **New method `is_stale()`**: Checks if status has been PENDING > 2 minutes or PROCESSING > 5 minutes
2. **New method `reset_if_stale()`**: Resets stale status to ERROR with user-friendly message
3. **Updated views**: `profile_view`, `census_section_view`, `referral_row_view`, and `referidos_view` now call `reset_if_stale()` before rendering

```python
def is_stale(self, pending_timeout_minutes=2, processing_timeout_minutes=5):
    # Uses user.date_joined for PENDING, fetched_at for PROCESSING
    ...

def reset_if_stale(self):
    if self.is_stale():
        self.status = self.Status.ERROR
        self.error_message = 'La verificación tardó demasiado. Por favor, intenta de nuevo.'
        self.save(update_fields=['status', 'error_message'])
        return True
    return False
```

### User Experience
- After 2-5 minutes of no progress, status automatically resets to ERROR
- User sees "Error" status with message explaining what happened
- Leader can click refresh button to retry

### Files Changed
- `___/accounts/models.py` (added `is_stale()` and `reset_if_stale()` methods)
- `___/accounts/views.py` (added stale checks in 4 views)

---

## Bug #6: Referidos page doesn't auto-update pending row statuses

**Milestone:** v1.3 Async Background Jobs
**Date:** 2026-01-21
**Status:** RESOLVED

### Symptom
On the referidos page, when a new referral registers and their cedula validation is processing, the leader must manually refresh the entire page to see the updated status. The row status badge shows "Pendiente" with a spinner but never updates automatically.

### Root Cause
The referidos page had no HTMX polling mechanism for pending rows. Unlike the profile page (which polls for the user's own status), the referidos table was completely static after initial load.

### Fix
Implemented batch polling with HTMX out-of-band (OOB) swaps:

1. **New endpoint `pending_referrals_view`**: Returns all PENDING/PROCESSING referral rows with `hx-swap-oob="true"` for in-place updates
2. **New partial `_pending_referrals.html`**: Renders updated rows with OOB swap attributes plus a self-replacing polling trigger
3. **Polling trigger in `referidos.html`**: Hidden div that polls every 5 seconds if pending rows exist

**Polling behavior:**
- Only rows with PENDING/PROCESSING status are fetched and updated
- Each row stops updating once it reaches a final status (ACTIVE, ERROR, etc.)
- Polling stops entirely when no rows are pending
- 5-second interval (same as profile page)

```html
<!-- Polling trigger - self-replaces to continue or stop polling -->
<div id="pending-poll-trigger"
     hx-get="{% url 'pending_referrals' %}"
     hx-trigger="load delay:5s"
     hx-swap="outerHTML">
</div>
```

### Files Changed
- `___/accounts/views.py` (added `pending_referrals_view`, updated `referidos_view` to pass `has_pending`)
- `___/accounts/urls.py` (added `/referidos/pending/` route)
- `___/templates/partials/_pending_referrals.html` (new - OOB swap response)
- `___/templates/referidos.html` (added polling trigger)

---

## Bug #7: Multiple issues with status updates and user retry capability

**Milestone:** v1.3 Async Background Jobs
**Date:** 2026-01-21
**Status:** RESOLVED

### Symptoms
1. **No retry button for regular users**: When a user's cedula verification fails (ERROR status from stale timeout), they see the error message but have no way to retry. Only leaders could refresh.

2. **Referidos page doesn't update after status transition**: When a referral's status changes from PENDING to ERROR (e.g., via stale check when user views their profile), the leader's referidos page continues showing "Pendiente" because the polling only fetched PENDING/PROCESSING rows.

### Root Causes

**Issue 1**: The census section template only showed the refresh button when `is_leader` was true:
```django
{% if show_refresh and is_leader %}
```

**Issue 2**: The `pending_referrals_view` queried only rows with PENDING/PROCESSING status. If status changed to ERROR elsewhere (e.g., profile page stale check), the row was excluded from poll results and never updated.

### Fix

**Issue 1**: Added retry button for regular users when status is ERROR/TIMEOUT/BLOCKED:
```django
{% elif cedula_info and cedula_info.status == 'ERROR' ... %}
    <button>Reintentar verificacion</button>
{% endif %}
```

**Issue 2**: Changed polling approach to track specific row IDs:
1. Server returns `pending_ids` with list of PENDING/PROCESSING row IDs
2. Polling trigger includes `?ids=X,Y,Z` to request specific rows
3. Server fetches those rows regardless of current status
4. Rows that transitioned to ERROR are still returned and updated via OOB swap
5. Next poll only includes rows still in PENDING/PROCESSING state

**Issue 3 (follow-up)**: OOB swaps weren't replacing table rows correctly:
- `hx-swap-oob="true"` uses innerHTML by default
- For `<tr>` elements, innerHTML doesn't work - need to replace the entire element
- Changed to `hx-swap-oob="outerHTML"` on both main row and detail row

**Issue 4 (2026-01-22)**: OOB swaps still not working after outerHTML fix:
- **Root Cause**: Browser HTML parser mangles naked `<tr>` elements outside of `<table>` context
- When HTMX receives the response, the browser parses it before HTMX can process OOB swaps
- Browsers "fix" orphan `<tr>` elements by wrapping or discarding them
- **Fix**: Wrapped `<tr>` elements in `<template>` tags in `_pending_referrals.html`
- The `<template>` tag preserves contents exactly without browser modification
- HTMX specifically looks inside `<template>` tags for OOB swap content

### Files Changed
- `___/templates/partials/_census_section.html` (added retry button for users)
- `___/accounts/views.py` (updated `referidos_view` and `pending_referrals_view` to track/accept IDs)
- `___/templates/referidos.html` (pass pending_ids to poll trigger)
- `___/templates/partials/_pending_referrals.html` (include pending_ids in next poll URL, wrap `<tr>` in `<template>` tags)

---

## Bug #8: Registration tasks fail with "Function not defined" while manual refresh works

**Milestone:** v1.3 Async Background Jobs
**Date:** 2026-01-22
**Status:** RESOLVED

### Symptom
When registering new users, the Playwright browser (visible in DEBUG=True mode) never appeared for cedula validation. The task was queued but failed silently. Manual refresh button worked correctly and triggered the browser.

### Investigation
Database inspection revealed the registration tasks were in the Failure table:
```
validate_cedula_39 - FAILED at 23:28:03
validate_cedula_40 - FAILED at 23:40:54
north-pasta-india-echo - SUCCEEDED at 23:44:10 (manual refresh)
```

All failures had error: `Function accounts.tasks.validate_cedula is not defined`

### Root Cause
The multiprocessing `set_start_method('fork')` fix from Bug #3 was placed at line 68 of `settings.py`, after other imports (`pathlib`, `decouple`). By the time it executed, some import had already initialized the multiprocessing context with macOS's default `spawn` method.

With `spawn`, worker processes start fresh without the parent's `sys.path`, causing `pydoc.locate()` to fail when looking up task functions. The fix appeared to work for manual refresh due to timing/caching differences.

### Fix
Moved the multiprocessing code to the **very first lines** of `settings.py`, before ANY other imports:

```python
"""Django settings..."""

# CRITICAL: Set multiprocessing start method BEFORE any other imports
import multiprocessing
if multiprocessing.get_start_method(allow_none=True) != 'fork':
    try:
        multiprocessing.set_start_method('fork', force=True)
    except RuntimeError:
        pass

from pathlib import Path
from decouple import config, Csv
# ... rest of settings
```

### Verification
After fix:
- `python -c "import django; django.setup(); import multiprocessing; print(multiprocessing.get_start_method())"` → `fork`
- Registration tasks now trigger browser and complete successfully

### Files Changed
- `___/___/settings.py` (moved multiprocessing code to top, before all imports)

---

## Bug #9: Bulk refresh tasks fail with "Function not defined" due to zombie qcluster

**Milestone:** v1.3 Async Background Jobs
**Date:** 2026-01-23
**Status:** RESOLVED

### Symptom
Bulk refresh on referidos page queued tasks, but all failed with `Function accounts.tasks.validate_cedula is not defined`. No browser opened. All rows remained in loading state until they eventually updated to ERROR. Strangely, a single profile refresh task succeeded earlier in the same session.

### Investigation
1. Qcluster log showed first task processed successfully (tennis-timing-vegan-oranges)
2. Bulk tasks were enqueued (visible in Django server log) but never appeared in qcluster worker log
3. All bulk tasks ended up in Failure table with "Function not defined" error
4. `ps aux | grep qcluster` revealed an OLD qcluster process from Monday still running alongside the new one

### Root Cause
An old qcluster process from a previous session (Monday) was still running with corrupted worker state. When tasks were queued, some were picked up by the old zombie process whose worker couldn't locate the function (likely due to stale imports or crashed worker).

The first successful task happened to be processed by the new qcluster's worker, while subsequent tasks were processed by the old zombie process.

### Fix
Kill all qcluster processes before starting a new one:
```bash
pkill -9 -f "manage.py qcluster"
```

After killing the old process and restarting, all tasks (including bulk refresh) work correctly.

### Recommendation
Add a safeguard check in qcluster startup or create a helper script that kills existing processes before starting. Consider adding a startup warning in development if multiple qcluster processes are detected.

### Files Changed
None (operational fix, no code changes)

---

## Future Improvement: Don't refresh NOT_FOUND cedulas

**Type:** Enhancement (not a bug)
**Date:** 2026-01-23
**Status:** NOTED FOR FUTURE

### Context
During bug hunting Test 1, user noted: "we don't want to refresh in the case that 'Cedula no registrada en el censo electoral'"

### Rationale
If a cedula is NOT_FOUND in the Registraduría census, refreshing it will just return NOT_FOUND again. Unlike ERROR status (which might succeed on retry), NOT_FOUND is a definitive answer from the source.

### Current Behavior
- Checkboxes appear for rows with: ERROR, TIMEOUT, BLOCKED, NOT_FOUND, PENDING
- NOT_FOUND can be selected for bulk refresh

### Proposed Change
- Exclude NOT_FOUND status from bulk refresh checkbox visibility (same as ACTIVE/CANCELLED)
- Maybe show NOT_FOUND with a different styling to indicate it's a final state

### Implementation Location
- `___/templates/partials/_referral_row.html` - checkbox visibility condition
- `___/accounts/views.py:bulk_refresh_view` - skip NOT_FOUND in server-side loop (already skips ACTIVE/CANCELLED)

---
