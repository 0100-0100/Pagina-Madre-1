# Phase 14: Task Integration + Signals - Research

**Researched:** 2026-01-20
**Domain:** Django signals, transaction.on_commit, Django-Q2 async_task integration
**Confidence:** HIGH

## Summary

This phase wires the Playwright scraper (Phase 13) to Django-Q2 (Phase 11) via Django's `post_save` signal. The key challenge is avoiding race conditions where background tasks start before the database transaction commits. Django's `transaction.on_commit()` hook solves this by deferring task queuing until after the user registration transaction completes.

Django-Q2 does not have built-in exponential backoff for retries. The project requirements specify custom retry logic (3 attempts with 1min, 5min, 15min backoff), which must be implemented manually using Django-Q2's `schedule()` function to queue delayed retry tasks. The task function itself tracks retry count via the CedulaInfo model.

**Primary recommendation:** Use `@receiver(post_save, sender=CustomUser)` with `transaction.on_commit()` to queue the initial task. Implement custom retry logic in the task function using `schedule()` with `next_run` for exponential backoff. Only trigger on `created=True` to avoid re-queueing on user updates.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Django | 4.2.x | Signals, transaction.on_commit | Already in project |
| django-q2 | 1.9.0 | async_task, schedule for delayed tasks | Already configured (Phase 11) |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| functools.partial | stdlib | Pass arguments to on_commit callback | When passing user_id to task |
| datetime.timedelta | stdlib | Calculate retry delays | For schedule next_run times |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom retry logic | Django-Q2 max_attempts | No exponential backoff - only count-based |
| schedule() for delays | Celery countdown | Would require replacing Django-Q2 |
| post_save signal | Explicit call in view | Signal is cleaner, decoupled from view logic |

**Installation:**
```bash
# No additional packages needed - uses Django built-ins and existing django-q2
```

## Architecture Patterns

### Recommended Project Structure
```
accounts/
    apps.py             # Import signals in ready()
    signals.py          # NEW: post_save handler for CustomUser
    tasks.py            # UPDATE: Add validate_cedula task with retry logic
    models.py           # UPDATE: Add retry_count field to CedulaInfo
    scraper.py          # EXISTS: RegistraduriaScraper (Phase 13)
```

### Pattern 1: Signal Handler with on_commit
**What:** Queue background task only after registration transaction commits
**When to use:** Triggering async tasks from model save operations
**Example:**
```python
# accounts/signals.py
# Source: https://docs.djangoproject.com/en/4.2/topics/db/transactions/

from functools import partial
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from .models import CustomUser, CedulaInfo


@receiver(post_save, sender=CustomUser)
def queue_cedula_validation(sender, instance, created, **kwargs):
    """Queue cedula validation task when new user is created."""
    if not created:
        return  # Skip updates, only trigger on new users

    if kwargs.get('raw', False):
        return  # Skip fixture loading

    # Create CedulaInfo with PENDING status
    CedulaInfo.objects.create(user=instance, status=CedulaInfo.Status.PENDING)

    # Queue task AFTER transaction commits
    transaction.on_commit(
        partial(_queue_validation_task, instance.id)
    )


def _queue_validation_task(user_id):
    """Helper to queue the async task."""
    async_task(
        'accounts.tasks.validate_cedula',
        user_id,
        task_name=f'validate_cedula_{user_id}'
    )
```

### Pattern 2: Task with Manual Retry and Exponential Backoff
**What:** Task function that handles its own retry logic with scheduled delays
**When to use:** When Django-Q2's built-in retry doesn't support backoff
**Example:**
```python
# accounts/tasks.py
# Source: Manual implementation (Django-Q2 lacks native backoff)

import logging
from datetime import datetime, timedelta

from django.utils import timezone
from django_q.tasks import schedule

from .models import CedulaInfo, CustomUser
from .scraper import RegistraduriaScraper

logger = logging.getLogger('django-q')

# Backoff delays in seconds: 1min, 5min, 15min
RETRY_DELAYS = [60, 300, 900]
MAX_ATTEMPTS = 3

# Status codes that should NOT trigger retry
PERMANENT_STATUSES = {'found', 'not_found', 'cancelled'}


def validate_cedula(user_id, attempt=1):
    """
    Validate cedula via Registraduria scraper.

    Args:
        user_id: CustomUser.id to validate
        attempt: Current attempt number (1-based)
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        cedula_info = user.cedula_info
    except (CustomUser.DoesNotExist, CedulaInfo.DoesNotExist):
        logger.error("validate_cedula: User %s or CedulaInfo not found", user_id)
        return

    # Update status to SCRAPING (browser actively running)
    cedula_info.status = CedulaInfo.Status.PROCESSING
    cedula_info.save(update_fields=['status'])

    logger.info("validate_cedula: User %s, attempt %d/%d",
                user_id, attempt, MAX_ATTEMPTS)

    # Run scraper
    scraper = RegistraduriaScraper()
    result = scraper.scrape_cedula(user.cedula)

    # Process result
    status = result.get('status')

    if status == 'found':
        _handle_found(cedula_info, result)
    elif status == 'not_found':
        _handle_not_found(cedula_info)
    elif status == 'cancelled':
        _handle_cancelled(cedula_info, result)
    elif status in PERMANENT_STATUSES:
        # Shouldn't happen but handle gracefully
        pass
    else:
        # Retriable error: timeout, network_error, captcha_failed, parse_error, blocked
        _handle_retriable_error(cedula_info, result, user_id, attempt)


def _handle_found(cedula_info, result):
    """Update CedulaInfo with voting location data."""
    cedula_info.status = CedulaInfo.Status.ACTIVE
    cedula_info.departamento = result.get('departamento', '') or ''
    cedula_info.municipio = result.get('municipio', '') or ''
    cedula_info.puesto = result.get('puesto', '') or ''
    cedula_info.direccion = result.get('direccion', '') or ''
    cedula_info.mesa = result.get('mesa', '') or ''
    cedula_info.fetched_at = timezone.now()
    cedula_info.save()
    logger.info("validate_cedula: FOUND - %s", cedula_info.user.cedula)


def _handle_not_found(cedula_info):
    """Update CedulaInfo as not found in census."""
    cedula_info.status = CedulaInfo.Status.NOT_FOUND
    cedula_info.fetched_at = timezone.now()
    cedula_info.save()
    logger.info("validate_cedula: NOT_FOUND - %s", cedula_info.user.cedula)


def _handle_cancelled(cedula_info, result):
    """Update CedulaInfo with cancelled cedula data."""
    # Determine if deceased or other cancellation
    novedad = result.get('novedad', '') or ''
    if 'FALLECIDO' in novedad.upper() or 'MUERTE' in novedad.upper():
        cedula_info.status = CedulaInfo.Status.CANCELLED_DECEASED
    else:
        cedula_info.status = CedulaInfo.Status.CANCELLED_OTHER

    cedula_info.novedad = novedad
    cedula_info.resolucion = result.get('resolucion', '') or ''
    cedula_info.fecha_novedad = result.get('fecha_novedad', '') or ''
    cedula_info.fetched_at = timezone.now()
    cedula_info.save()
    logger.info("validate_cedula: CANCELLED - %s", cedula_info.user.cedula)


def _handle_retriable_error(cedula_info, result, user_id, attempt):
    """Handle retriable error: schedule retry or mark as ERROR."""
    error_status = result.get('status', 'error')
    error_msg = result.get('error', 'Unknown error')

    if attempt < MAX_ATTEMPTS:
        # Schedule retry with exponential backoff
        delay_seconds = RETRY_DELAYS[attempt - 1]  # 0-indexed
        next_run = timezone.now() + timedelta(seconds=delay_seconds)

        # Update status to show retrying
        cedula_info.retry_count = attempt
        cedula_info.error_message = f"Attempt {attempt}: {error_status} - {error_msg}"
        cedula_info.save(update_fields=['retry_count', 'error_message'])

        logger.warning(
            "validate_cedula: %s on attempt %d, scheduling retry in %ds",
            error_status, attempt, delay_seconds
        )

        # Schedule delayed retry
        schedule(
            'accounts.tasks.validate_cedula',
            user_id,
            attempt + 1,
            schedule_type='O',  # Once
            next_run=next_run,
            name=f'validate_cedula_retry_{user_id}_{attempt + 1}'
        )
    else:
        # Max attempts exhausted
        _mark_as_error(cedula_info, error_status, error_msg, result.get('raw_html'))


def _mark_as_error(cedula_info, error_status, error_msg, raw_html=None):
    """Mark CedulaInfo as ERROR after all retries exhausted."""
    if error_status == 'timeout':
        cedula_info.status = CedulaInfo.Status.TIMEOUT
    elif error_status == 'blocked':
        cedula_info.status = CedulaInfo.Status.BLOCKED
    else:
        cedula_info.status = CedulaInfo.Status.ERROR

    cedula_info.error_message = error_msg
    cedula_info.fetched_at = timezone.now()
    if raw_html:
        cedula_info.raw_response = raw_html
    cedula_info.save()
    logger.error("validate_cedula: ERROR after max attempts - %s",
                 cedula_info.user.cedula)
```

### Pattern 3: Signal Registration in AppConfig
**What:** Import signals module in AppConfig.ready() to register handlers
**When to use:** Always - this is the standard Django pattern
**Example:**
```python
# accounts/apps.py
# Source: https://docs.djangoproject.com/en/4.2/topics/signals/

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Import signals to register handlers
        from . import signals  # noqa: F401
```

### Anti-Patterns to Avoid
- **Queuing task directly in post_save:** Race condition - task may start before transaction commits
- **Passing model instance to task:** Instance may change; always pass ID and fetch fresh
- **Using Django-Q2 max_attempts for backoff:** Only limits count, no delay between retries
- **Triggering on updates:** Signal fires on every save(); must check `created=True`
- **Database queries in raw mode:** Skip signal when `raw=True` (fixture loading)

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Post-commit execution | Custom threading | transaction.on_commit() | Django handles transaction state |
| Model creation detection | Check pk before save | post_save `created` argument | Django provides this built-in |
| Delayed task execution | time.sleep() in task | schedule() with next_run | Non-blocking, persists in queue |
| Unique signal registration | Manual deduplication | dispatch_uid parameter | Django signal framework feature |

**Key insight:** Django's `transaction.on_commit()` is specifically designed for this use case. It handles nested transactions, rollbacks, and autocommit mode correctly.

## Common Pitfalls

### Pitfall 1: Race Condition Without on_commit
**What goes wrong:** Background task starts before user record is committed
**Why it happens:** post_save fires inside the transaction, not after commit
**How to avoid:** Always wrap async_task call in transaction.on_commit()
**Warning signs:** "DoesNotExist" errors in background task logs

### Pitfall 2: Triggering on Every Save
**What goes wrong:** Duplicate tasks queued when user profile is updated
**Why it happens:** post_save fires on both create and update
**How to avoid:** Check `if not created: return` at start of handler
**Warning signs:** Multiple PENDING CedulaInfo records for same user

### Pitfall 3: Passing Instance Instead of ID
**What goes wrong:** Task uses stale data or pickle errors
**Why it happens:** Instance may change between queue and execution
**How to avoid:** Pass `instance.id` and fetch fresh in task
**Warning signs:** Inconsistent data, serialization errors

### Pitfall 4: Missing CedulaInfo Creation
**What goes wrong:** Task fails because CedulaInfo doesn't exist
**Why it happens:** CedulaInfo not created before task queued
**How to avoid:** Create CedulaInfo in signal handler before on_commit
**Warning signs:** "RelatedObjectDoesNotExist" errors in task

### Pitfall 5: Infinite Retry Loop
**What goes wrong:** Task keeps retrying forever
**Why it happens:** Retry logic doesn't check attempt count properly
**How to avoid:** Pass attempt number as argument, check against MAX_ATTEMPTS
**Warning signs:** Thousands of scheduled tasks for same user

### Pitfall 6: Testing on_commit Callbacks
**What goes wrong:** Callbacks never execute in tests
**Why it happens:** Django TestCase wraps tests in transactions that roll back
**How to avoid:** Use `TestCase.captureOnCommitCallbacks()` or `TransactionTestCase`
**Warning signs:** Tests pass but callbacks don't run

## Code Examples

Verified patterns from official sources:

### Complete Signal Module
```python
# accounts/signals.py
# Source: https://docs.djangoproject.com/en/4.2/topics/signals/
# Source: https://docs.djangoproject.com/en/4.2/topics/db/transactions/

import logging
from functools import partial

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from .models import CedulaInfo, CustomUser

logger = logging.getLogger('django-q')


@receiver(post_save, sender=CustomUser, dispatch_uid='queue_cedula_validation')
def queue_cedula_validation(sender, instance, created, raw, **kwargs):
    """
    Queue cedula validation task when new user is created.

    Uses transaction.on_commit() to ensure task is queued only after
    the user registration transaction successfully commits.

    Args:
        sender: CustomUser model class
        instance: The saved CustomUser instance
        created: True if new user, False if update
        raw: True if loading fixtures
    """
    if not created:
        return  # Only trigger on new user creation

    if raw:
        return  # Skip when loading fixtures

    # Create CedulaInfo record with PENDING status
    # This happens inside the transaction
    CedulaInfo.objects.create(
        user=instance,
        status=CedulaInfo.Status.PENDING,
        retry_count=0
    )

    logger.info("CedulaInfo created for user %s, queueing validation task",
                instance.cedula)

    # Queue async task AFTER transaction commits
    # Using partial to pass user_id
    transaction.on_commit(
        partial(_queue_validation_task, instance.id),
        using='default'
    )


def _queue_validation_task(user_id):
    """
    Helper function to queue the validation task.

    Called by on_commit after transaction commits successfully.
    """
    task_id = async_task(
        'accounts.tasks.validate_cedula',
        user_id,
        task_name=f'validate_cedula_{user_id}'
    )
    logger.info("Queued validate_cedula task %s for user_id=%s", task_id, user_id)
```

### Delayed Task Scheduling for Retry
```python
# Using schedule() for exponential backoff retry
# Source: https://django-q2.readthedocs.io/en/master/schedules.html

from datetime import timedelta
from django.utils import timezone
from django_q.tasks import schedule

def schedule_retry(user_id, attempt, delay_seconds):
    """Schedule a retry task with delay."""
    next_run = timezone.now() + timedelta(seconds=delay_seconds)

    schedule(
        'accounts.tasks.validate_cedula',  # Function path
        user_id,                            # Positional arg
        attempt,                            # Positional arg (attempt number)
        schedule_type='O',                  # Once
        next_run=next_run,                  # When to run
        name=f'retry_cedula_{user_id}_{attempt}'  # Unique name
    )
```

### Model Migration for retry_count Field
```python
# accounts/migrations/0007_cedulainfo_retry_count.py
# Generated migration for adding retry_count field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_customuser_role'),  # Adjust to actual last migration
    ]

    operations = [
        migrations.AddField(
            model_name='cedulainfo',
            name='retry_count',
            field=models.PositiveSmallIntegerField(
                default=0,
                verbose_name='Intentos de reintento'
            ),
        ),
    ]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Direct async call in signal | transaction.on_commit() | Django 1.9 | Prevents race conditions |
| Celery countdown for delays | Django-Q2 schedule() | N/A (different stack) | Use schedule for delayed execution |
| Storing retry count in task | Store in model | Best practice | Persists across restarts |

**Deprecated/outdated:**
- Calling async_task directly in post_save without on_commit: Causes race conditions
- Using sync=True for testing: Use captureOnCommitCallbacks() instead

## Open Questions

Things that couldn't be fully resolved:

1. **Django-Q2 Native Backoff Support**
   - What we know: Feature request exists (GitHub issue #480) but not implemented
   - What's unclear: Whether future versions will add this
   - Recommendation: Implement manual backoff using schedule() as shown

2. **Browser Cleanup Between Retries**
   - What we know: Scraper uses browser singleton with fresh context per scrape
   - What's unclear: Whether browser should be restarted between retry attempts
   - Recommendation: Let singleton pattern handle it; browser recycles after recycle=100 tasks

3. **Concurrent Registration Edge Case**
   - What we know: Single worker (workers=1) prevents concurrent task execution
   - What's unclear: What happens if two users register simultaneously
   - Recommendation: SQLite WAL + single worker already handles this; tasks queue sequentially

## Sources

### Primary (HIGH confidence)
- [Django Signals Documentation](https://docs.djangoproject.com/en/4.2/topics/signals/) - Signal registration, receiver decorator
- [Django Transaction Documentation](https://docs.djangoproject.com/en/4.2/topics/db/transactions/) - on_commit() usage
- [Django Model Signals Reference](https://docs.djangoproject.com/en/4.2/ref/signals/) - post_save arguments
- [Django-Q2 Schedules Documentation](https://django-q2.readthedocs.io/en/master/schedules.html) - schedule() function

### Secondary (MEDIUM confidence)
- [Django-Q2 Tasks Documentation](https://django-q2.readthedocs.io/en/master/tasks.html) - async_task parameters
- [Django Async Job Database Fix](https://spapas.github.io/2019/02/25/django-fix-async-db/) - on_commit pattern explanation
- [Django-Q Backoff Feature Request](https://github.com/Koed00/django-q/issues/480) - Confirms no native backoff

### Tertiary (LOW confidence)
- Various blog posts confirming best practices (cross-referenced with official docs)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Uses Django built-ins and existing django-q2
- Architecture: HIGH - Official Django documentation patterns
- Pitfalls: HIGH - Common issues documented in Django docs and community
- Retry logic: MEDIUM - Manual implementation due to lack of native Django-Q2 support

**Research date:** 2026-01-20
**Valid until:** 60 days (stable Django patterns)
