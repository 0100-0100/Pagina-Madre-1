# Phase 11: Django-Q2 Foundation - Research

**Researched:** 2026-01-19
**Domain:** Django background task queue with SQLite
**Confidence:** HIGH

## Summary

Django-Q2 1.9.0 provides a robust task queue infrastructure for Django applications. For SQLite-based deployments, the ORM broker is the correct choice with single-worker configuration to prevent database locking. WAL (Write-Ahead Logging) mode must be enabled to allow concurrent reads during writes.

The admin interface provides separate views for successful tasks, failed tasks, scheduled tasks, and queued tasks (ORM broker only). Customization is straightforward via standard Django admin patterns: unregister defaults and register custom ModelAdmin classes. The Task model includes `time_taken()` for duration, `attempt_count` for retry tracking, and `result` for error details.

**Primary recommendation:** Install django-q2 with ORM broker, enable WAL mode via connection signal, configure Django logging for verbose output when DEBUG=True, and verify with a simple test task.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| django-q2 | 1.9.0 | Background task queue | Fork of Django-Q with active maintenance, Python 3.9-3.13, Django 4.2-6.0 support |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| N/A | - | ORM broker is built-in | SQLite deployments, no external dependencies |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| ORM broker | Redis broker | Redis requires external service, better for multi-worker (PostgreSQL needed) |
| django-q2 | Celery | Celery is heavier, requires Redis/RabbitMQ, overkill for <100 users |
| django-q2 | Huey | Smaller community, less Django admin integration |

**Installation:**
```bash
pip install django-q2==1.9.0
```

## Architecture Patterns

### Recommended Project Structure
```
___/
├── settings.py         # Q_CLUSTER config, WAL mode signal
└── db_signals.py       # Optional: WAL mode signal if separated

accounts/
├── apps.py             # Import db_signals in ready() if separated
└── tasks.py            # Task functions (future phases)
```

### Pattern 1: Q_CLUSTER Configuration for SQLite
**What:** Configure Django-Q2 for SQLite with ORM broker
**When to use:** SQLite database with single-worker constraint
**Example:**
```python
# settings.py
# Source: https://django-q2.readthedocs.io/en/latest/configure.html

Q_CLUSTER = {
    'name': 'pagina-madre',
    'workers': 1,  # CRITICAL: SQLite cannot handle concurrent writes
    'timeout': 120,  # 2 minutes max per task
    'retry': 180,  # Must exceed timeout (3 minutes)
    'queue_limit': 50,  # Tasks kept in memory
    'save_limit': 250,  # Successful tasks to keep in DB
    'orm': 'default',  # Use Django's default database as broker
    'recycle': 100,  # Restart worker after 100 tasks (prevent memory leaks)
    'ack_failures': True,  # Mark failed tasks as acknowledged
    'max_attempts': 3,  # Limit retry attempts
    'label': 'Django Q2',  # Admin page label
}
```

### Pattern 2: WAL Mode via Connection Signal
**What:** Enable SQLite Write-Ahead Logging to prevent database locking
**When to use:** Any SQLite deployment with concurrent access (web server + qcluster)
**Example:**
```python
# settings.py (at the end, after DATABASES definition)
# Source: https://djangoandy.com/2024/07/08/enabling-wal-in-sqlite-in-django/

from django.db.backends.signals import connection_created
from django.dispatch import receiver

@receiver(connection_created)
def enable_sqlite_wal(sender, connection, **kwargs):
    """Enable WAL mode for SQLite to prevent database locking."""
    if connection.vendor == 'sqlite':
        cursor = connection.cursor()
        cursor.execute('PRAGMA journal_mode=WAL;')
        cursor.execute('PRAGMA busy_timeout=5000;')
        cursor.close()
```

### Pattern 3: DEBUG-Aware Logging Configuration
**What:** Verbose logging when DEBUG=True, minimal in production
**When to use:** All deployments
**Example:**
```python
# settings.py
# Source: https://github.com/Koed00/django-q/issues/268

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} [{name}] {levelname} {message}',
            'style': '{',
            'datefmt': '%H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django-q': {  # NOTE: hyphen, not underscore!
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
```

### Pattern 4: Admin Customization for Task Monitoring
**What:** Extend default admin to show duration, retry count, error details
**When to use:** When detailed task monitoring is needed
**Example:**
```python
# accounts/admin.py (or separate admin file)
# Source: https://django-q2.readthedocs.io/en/master/admin.html

from django.contrib import admin
from django_q import models as q_models
from django_q import admin as q_admin

# Unregister default admins
admin.site.unregister([q_models.Failure])

@admin.register(q_models.Failure)
class FailureAdmin(q_admin.FailAdmin):
    """Enhanced failed task admin with attempt count and error details."""
    list_display = (
        'name',
        'func',
        'started',
        'stopped',
        'time_taken',
        'attempt_count',
        'short_result',  # Error message
    )
    list_filter = ('group', 'cluster', 'started')
```

### Anti-Patterns to Avoid
- **Multiple workers with SQLite:** Causes "database is locked" errors. Always use `workers=1`.
- **retry <= timeout:** Task will retry before timeout, causing duplicates. Always ensure `retry > timeout`.
- **Forgetting WAL mode:** Web server and qcluster will conflict on writes without WAL.
- **Logger name with underscore:** Logger is `django-q` (hyphen), not `django_q` (underscore).

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Task queue | Custom threading/subprocess | Django-Q2 | Handles failures, retries, admin, persistence |
| Task monitoring | Custom status page | Django-Q2 Admin | Built-in Success/Failure views with resubmit |
| SQLite concurrency | Custom locking | WAL mode | Proven SQLite feature, one PRAGMA command |
| Task serialization | JSON serialization | Pickling (built-in) | Django-Q2 uses PickledObjectField |

**Key insight:** Django-Q2 provides complete infrastructure. Don't reinvent task status tracking, retry logic, or admin views.

## Common Pitfalls

### Pitfall 1: Missing WAL Mode
**What goes wrong:** "database is locked" errors under concurrent access
**Why it happens:** SQLite default journal mode blocks all reads during writes
**How to avoid:** Enable WAL via connection_created signal (see Pattern 2)
**Warning signs:** Intermittent 500 errors when qcluster and web server both active

### Pitfall 2: Wrong Logger Name
**What goes wrong:** Django-Q2 logs don't appear in configured handlers
**Why it happens:** Import is `django_q` (underscore), but logger name is `django-q` (hyphen)
**How to avoid:** Use `'django-q'` in LOGGING configuration
**Warning signs:** No qcluster output despite DEBUG level logging

### Pitfall 3: Retry Less Than Timeout
**What goes wrong:** Tasks retry before completion, causing duplicates
**Why it happens:** Broker assumes task failed if not acknowledged within retry window
**How to avoid:** Ensure `retry` > `timeout` (e.g., timeout=120, retry=180)
**Warning signs:** Same task appearing multiple times in Success/Failure

### Pitfall 4: sync=True in Production
**What goes wrong:** Tasks block request/response cycle, defeating async purpose
**Why it happens:** sync mode is convenient for testing, accidentally left enabled
**How to avoid:** Never use global sync setting; only use sync=True in specific test calls
**Warning signs:** Slow page loads, requests timing out

### Pitfall 5: Forgetting to Run qcluster
**What goes wrong:** Tasks queue but never execute
**Why it happens:** Developer forgets to start worker in separate terminal
**How to avoid:** Document workflow clearly, verify with test task
**Warning signs:** Tasks stuck in Queued Tasks admin, never moving to Success/Failure

## Code Examples

Verified patterns from official sources:

### Verification Test Task
```python
# Shell verification: test Django-Q2 is working
# Source: https://django-q2.readthedocs.io/en/master/tasks.html

# Terminal 1: Start qcluster
# python manage.py qcluster

# Terminal 2: Django shell
from django_q.tasks import async_task, result

# Queue a simple test task
task_id = async_task('math.floor', 2.5)
print(f"Task queued: {task_id}")

# Wait for result (up to 5 seconds)
import time
time.sleep(2)  # Give qcluster time to process

# Check result
from django_q.models import Task
task = Task.objects.get(id=task_id)
print(f"Success: {task.success}")
print(f"Result: {task.result}")
print(f"Duration: {task.time_taken()}s")
```

### Custom Echo Task for Verification
```python
# accounts/tasks.py (or dedicated tasks file)

def echo_test(message):
    """Simple test task to verify Django-Q2 is working."""
    import logging
    logger = logging.getLogger('django-q')
    logger.info(f"Echo task executed: {message}")
    return f"Echo: {message}"
```

```python
# Shell usage
from django_q.tasks import async_task

task_id = async_task('accounts.tasks.echo_test', 'Hello Django-Q2!')
```

### INSTALLED_APPS Addition
```python
# settings.py
INSTALLED_APPS = [
    'accounts',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_q',  # Add django-q2
]
```

## Admin Model Reference

Django-Q2 registers these admin models automatically:

| Model | Purpose | Key list_display Fields |
|-------|---------|------------------------|
| Success | Completed tasks | name, group, func, cluster, started, stopped, time_taken |
| Failure | Failed tasks | name, group, func, cluster, started, stopped, short_result |
| Schedule | Scheduled tasks | id, name, func, schedule_type, repeats, cluster, next_run |
| OrmQ | Queued tasks (ORM broker only) | id, key, name, group, func, lock, task_id |

**Task Model Fields Available for Customization:**
- `id`: Task UUID (CharField, 32 chars)
- `name`: Task name (CharField, 100 chars)
- `func`: Function path (CharField, 256 chars)
- `args`, `kwargs`: Task arguments (PickledObjectField)
- `result`: Return value or error (PickledObjectField)
- `group`: Task grouping (CharField, nullable)
- `cluster`: Cluster name (CharField, nullable)
- `started`, `stopped`: Timestamps (DateTimeField)
- `success`: Completion status (BooleanField)
- `attempt_count`: Retry attempts (IntegerField)
- `time_taken()`: Method returning duration in seconds

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Django-Q (unmaintained) | Django-Q2 | June 2021 | Django-Q2 is actively maintained fork |
| Manual PRAGMA execution | Django 5.1 init_command | Django 5.1 | Native WAL support in settings (project uses Django 4.2, so signal approach needed) |

**Deprecated/outdated:**
- Django-Q (original): Unmaintained since June 2021, use Django-Q2 instead
- Manual WAL commands: For Django 5.1+, use `init_command` in DATABASES OPTIONS

## Upgrade Path Documentation

Include this comment block in settings.py for future scaling:

```python
# Django-Q2 Configuration
# ========================
# Current: SQLite + ORM broker (suitable for <100 users, single worker)
#
# UPGRADE PATH for PostgreSQL + Redis (when needed):
# 1. Install: pip install redis
# 2. Replace 'orm': 'default' with:
#    'redis': {
#        'host': 'localhost',
#        'port': 6379,
#        'db': 0,
#    }
# 3. Increase 'workers' to match CPU cores
# 4. Remove WAL mode signal (PostgreSQL handles concurrency natively)
# 5. Consider separate broker database for high-throughput scenarios
```

## Open Questions

Things that couldn't be fully resolved:

1. **Python 3.14 Compatibility**
   - What we know: Django-Q2 officially supports Python 3.9-3.13
   - What's unclear: Whether 3.14 will work (untested)
   - Recommendation: Test when upgrading Python, expect it to work

2. **WAL Mode Persistence**
   - What we know: WAL mode is database-level, persists once set
   - What's unclear: Whether signal re-execution on every connection is wasteful
   - Recommendation: Signal approach is safe and idempotent, no action needed

## Sources

### Primary (HIGH confidence)
- [Django-Q2 Official Docs](https://django-q2.readthedocs.io/) - Configuration, admin, tasks
- [Django-Q2 GitHub admin.py](https://github.com/django-q2/django-q2/blob/master/django_q/admin.py) - Admin class definitions
- [Django-Q2 GitHub models.py](https://github.com/django-q2/django-q2/blob/master/django_q/models.py) - Task model fields

### Secondary (MEDIUM confidence)
- [Django Andy WAL Mode Guide](https://djangoandy.com/2024/07/08/enabling-wal-in-sqlite-in-django/) - WAL mode signal pattern
- [Django-Q GitHub Issue #268](https://github.com/Koed00/django-q/issues/268) - Logger name clarification
- [Django-Q GitHub Issue #209](https://github.com/Koed00/django-q/issues/209) - Logging architecture

### Tertiary (LOW confidence)
- N/A - All findings verified with primary or secondary sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official documentation, PyPI verified
- Architecture: HIGH - Official docs + community patterns confirmed
- Pitfalls: HIGH - GitHub issues and official docs confirm all pitfalls
- Admin customization: HIGH - Source code inspection confirms patterns

**Research date:** 2026-01-19
**Valid until:** 60 days (stable library, infrequent updates)
