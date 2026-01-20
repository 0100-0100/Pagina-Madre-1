# Architecture Research: v1.3 Async Background Jobs

**Domain:** Django background task processing + web scraping integration
**Researched:** 2026-01-19
**Confidence:** HIGH (based on official Django-Q2 docs and Playwright documentation)

## Executive Summary

Integrating Django-Q2 background tasks with Playwright scraping into the existing Django auth portal requires:

1. **Minimal modifications** to existing code (add signal in AppConfig, add new model)
2. **New components** isolated in dedicated modules (tasks.py, scrapers.py)
3. **Separate worker process** running alongside Django (`python manage.py qcluster`)
4. **Playwright per-task instantiation** (cannot share browser instances across workers)

The architecture follows Django-Q2's recommended pattern: signal triggers `async_task()`, worker executes scraper, result stored in model.

## Integration Points

### Existing Components to Modify

| File | Modification | Reason |
|------|--------------|--------|
| `___/___/settings.py` | Add `django_q` to INSTALLED_APPS, add Q_CLUSTER config | Enable Django-Q2 |
| `___/accounts/apps.py` | Import signals in `ready()` | Register post_save handler |
| `___/accounts/urls.py` | Add 1 new URL pattern | Manual refresh endpoint |
| `___/accounts/views.py` | Add 1 new view function | Trigger manual refresh |
| `___/accounts/admin.py` | Register CedulaInfo model | Admin visibility |

### Existing Components Unchanged

| Component | Why Unchanged |
|-----------|---------------|
| `CustomUser` model | CedulaInfo has FK to User, not vice versa |
| `middleware.py` | No changes to auth flow |
| All templates | v1.3 is backend-only; UI comes in v1.4 |
| `forms.py` | Registration form unchanged |
| `register` view | Signal handles task trigger automatically |

### Connection Flow

```
User registers
    |
    v
CustomUser.save() executes
    |
    v
post_save signal fires
    |
    v
Signal handler calls async_task('accounts.tasks.fetch_cedula_info', user_id)
    |
    v
Task queued in django_q_ormq table
    |
    v
qcluster worker picks up task
    |
    v
Worker runs fetch_cedula_info(user_id)
    |
    v
Task creates Playwright browser, scrapes, stores CedulaInfo
```

## New Components

### 1. CedulaInfo Model (`accounts/models.py`)

```python
class CedulaInfo(models.Model):
    """Scraped cedula data from Registraduria."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        FOUND = 'found', 'Encontrada'
        NOT_FOUND = 'not_found', 'No encontrada'
        CANCELLED = 'cancelled', 'Cancelada'
        ERROR = 'error', 'Error'

    user = models.OneToOneField(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='cedula_info'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    # Voting location fields (nullable - may not exist)
    departamento = models.CharField(max_length=100, blank=True)
    municipio = models.CharField(max_length=100, blank=True)
    puesto = models.CharField(max_length=200, blank=True)
    direccion = models.CharField(max_length=300, blank=True)
    mesa = models.CharField(max_length=20, blank=True)

    # Metadata
    raw_response = models.TextField(blank=True)  # Full scraped text for debugging
    error_message = models.TextField(blank=True)

    fetched_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Informacion de Cedula'
        verbose_name_plural = 'Informaciones de Cedula'
```

**Rationale:**
- OneToOne relationship keeps User model clean
- Status enum handles all known Registraduria response states
- `raw_response` aids debugging without polluting structured fields
- Timestamps enable refresh age checking

### 2. Signals Module (`accounts/signals.py`)

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def trigger_cedula_fetch(sender, instance, created, **kwargs):
    """Queue cedula info fetch for new users."""
    if created:
        async_task(
            'accounts.tasks.fetch_cedula_info',
            instance.id,
            task_name=f'fetch_cedula_{instance.cedula}'
        )
```

**Rationale:**
- Only triggers on `created=True` (new registrations)
- Passes `user.id` not user object (serialization safety)
- Named task for admin visibility

### 3. Tasks Module (`accounts/tasks.py`)

```python
from django.utils import timezone
from .models import CustomUser, CedulaInfo
from .scrapers import scrape_registraduria

def fetch_cedula_info(user_id):
    """
    Background task to fetch cedula info from Registraduria.

    Called by:
    - post_save signal on user creation
    - manual refresh view
    """
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return {'error': 'User not found', 'user_id': user_id}

    # Get or create CedulaInfo record
    cedula_info, _ = CedulaInfo.objects.get_or_create(user=user)
    cedula_info.status = CedulaInfo.Status.PENDING
    cedula_info.save()

    # Execute scraper
    result = scrape_registraduria(user.cedula)

    # Update record based on result
    cedula_info.status = result['status']
    cedula_info.fetched_at = timezone.now()

    if result['status'] == CedulaInfo.Status.FOUND:
        cedula_info.departamento = result.get('departamento', '')
        cedula_info.municipio = result.get('municipio', '')
        cedula_info.puesto = result.get('puesto', '')
        cedula_info.direccion = result.get('direccion', '')
        cedula_info.mesa = result.get('mesa', '')
    elif result['status'] == CedulaInfo.Status.ERROR:
        cedula_info.error_message = result.get('error', '')

    cedula_info.raw_response = result.get('raw', '')
    cedula_info.save()

    return {
        'user_id': user_id,
        'cedula': user.cedula,
        'status': result['status']
    }
```

**Rationale:**
- Idempotent (can be safely retried)
- Returns structured result for task monitoring
- Separates orchestration (task) from scraping (scraper)

### 4. Scrapers Module (`accounts/scrapers.py`)

```python
from playwright.sync_api import sync_playwright
from .models import CedulaInfo

def scrape_registraduria(cedula: str) -> dict:
    """
    Scrape Registraduria for cedula voting location.

    Returns dict with:
    - status: CedulaInfo.Status value
    - departamento, municipio, puesto, direccion, mesa (if found)
    - error: error message (if error)
    - raw: full page text for debugging

    IMPORTANT: Creates new Playwright instance per call.
    Cannot reuse browser across worker threads.
    """
    result = {
        'status': CedulaInfo.Status.ERROR,
        'raw': '',
        'error': ''
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Navigate to Registraduria consultation page
            page.goto('https://wsp.registraduria.gov.co/certificado/')

            # Fill cedula field and submit
            page.fill('input[name="nuip"]', cedula)
            page.click('button[type="submit"]')

            # Wait for result
            page.wait_for_load_state('networkidle')

            # Extract content
            content = page.content()
            result['raw'] = page.inner_text('body')

            # Parse result based on page content
            # (Actual parsing logic depends on page structure)
            if 'no se encuentra' in result['raw'].lower():
                result['status'] = CedulaInfo.Status.NOT_FOUND
            elif 'cancelada' in result['raw'].lower():
                result['status'] = CedulaInfo.Status.CANCELLED
            else:
                # Parse voting location fields
                # This is placeholder - actual selectors TBD
                result['status'] = CedulaInfo.Status.FOUND
                # result['departamento'] = page.inner_text('.departamento')
                # ... etc

            browser.close()

    except Exception as e:
        result['status'] = CedulaInfo.Status.ERROR
        result['error'] = str(e)

    return result
```

**Critical Architecture Note:** Each task invocation creates a fresh Playwright browser instance. Per [Playwright GitHub Issue #1207](https://github.com/microsoft/playwright-python/issues/1207), browser instances cannot be shared across threads or processes.

### 5. Manual Refresh View (`accounts/views.py`)

```python
@login_required
def refresh_cedula_info(request):
    """Manually trigger cedula info refresh."""
    from django_q.tasks import async_task

    async_task(
        'accounts.tasks.fetch_cedula_info',
        request.user.id,
        task_name=f'manual_refresh_{request.user.cedula}'
    )

    messages.info(request, 'Actualizando informacion de cedula...')
    return redirect('home')
```

### 6. URL Pattern (`accounts/urls.py`)

```python
path('actualizar-cedula/', refresh_cedula_info, name='refresh_cedula'),
```

## Data Flow

### Registration Flow (Automatic Trigger)

```
                          Django Process                    Worker Process
                    +-----------------------+          +-------------------+
                    |                       |          |                   |
User submits  ---->| register view         |          |  qcluster         |
registration       | form.save()           |          |  worker pool      |
                   | CustomUser created    |          |                   |
                   |        |              |          |                   |
                   |        v              |          |                   |
                   | post_save signal      |          |                   |
                   | async_task() called   |------>   |  Task queued in   |
                   |        |              |  ORM     |  django_q_ormq    |
                   |        v              | broker   |        |          |
                   | Response returned     |          |        v          |
                   | (user logged in)      |          |  Worker picks up  |
                   |                       |          |  fetch_cedula_info|
                   +-----------------------+          |        |          |
                                                      |        v          |
                                                      |  Playwright       |
                                                      |  scrapes page     |
                                                      |        |          |
                                                      |        v          |
                                                      |  CedulaInfo       |
                                                      |  model updated    |
                                                      +-------------------+
```

### Manual Refresh Flow

```
User clicks       Django Process           Worker Process
"Refresh"   --->  refresh_cedula view --->  Same as above
                  async_task()
                  redirect with message
```

## Django-Q2 Worker Setup

### Settings Configuration

```python
# ___/___/settings.py

INSTALLED_APPS = [
    'accounts',
    'django_q',  # Add this
    # ... rest of apps
]

Q_CLUSTER = {
    'name': 'PaginaMadre',
    'workers': 2,          # Conservative for SQLite
    'timeout': 120,        # 2 min for slow scrapes
    'retry': 180,          # Retry after 3 min
    'queue_limit': 10,
    'bulk': 5,
    'orm': 'default',      # Use SQLite via ORM broker
    'poll': 1,             # 1 second poll interval
    'catch_up': False,     # Don't run missed scheduled tasks
}
```

**SQLite Considerations:**
- Keep `workers` low (2-4) to avoid database lock contention
- The ORM broker stores tasks in `django_q_ormq` table
- Task results stored in `django_q_task` table
- Both visible in Django Admin

### Running the Worker

**Development (two terminal windows):**

```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Task worker
python manage.py qcluster
```

**Production (supervisor/systemd):**

```ini
# /etc/supervisor/conf.d/pagina_madre_worker.conf
[program:pagina_madre_worker]
command=/path/to/venv/bin/python manage.py qcluster
directory=/path/to/___
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/pagina_madre_worker.log
```

### Sync Mode for Testing

```python
# settings.py (test environment)
Q_CLUSTER = {
    # ... other settings
    'sync': True,  # Execute tasks synchronously
}
```

This bypasses the worker process and executes tasks inline, useful for unit tests.

## Suggested Build Order

Based on dependency analysis, recommended phase sequence:

### Phase 1: Django-Q2 Foundation
1. Install `django-q2` package
2. Add to INSTALLED_APPS with Q_CLUSTER config
3. Run migrations (`django_q` creates its tables)
4. Verify qcluster starts without errors
5. Test async_task with simple function

**Rationale:** Establish infrastructure before building on it.

### Phase 2: CedulaInfo Model
1. Create CedulaInfo model with all fields
2. Generate and run migration
3. Register in admin
4. Verify in Django shell

**Rationale:** Model must exist before tasks can write to it.

### Phase 3: Scraper Implementation
1. Install `playwright` package
2. Run `playwright install chromium`
3. Create scrapers.py with scrape_registraduria function
4. Test scraper standalone (not as task)
5. Handle all response states (found, not_found, cancelled, error)

**Rationale:** Isolate scraping logic for easier testing/debugging.

### Phase 4: Task Integration
1. Create tasks.py with fetch_cedula_info
2. Test task via Django shell: `async_task('accounts.tasks.fetch_cedula_info', user_id)`
3. Verify CedulaInfo updated correctly
4. Check task in admin (django_q_task table)

**Rationale:** Integration requires working scraper and model.

### Phase 5: Signal Wiring
1. Create signals.py with post_save handler
2. Update apps.py to import signals in ready()
3. Test: create user, verify task queued automatically
4. Verify CedulaInfo created with correct data

**Rationale:** Signal depends on working task.

### Phase 6: Manual Refresh Endpoint
1. Add refresh_cedula_info view
2. Add URL pattern
3. Test: logged in user can trigger refresh
4. Verify task queued and CedulaInfo updated

**Rationale:** Secondary trigger, depends on working task.

## Component Diagram

```
+---------------------------+
|    Django Application     |
|---------------------------|
|  accounts/                |
|  +- models.py             |
|  |   +- CustomUser        |
|  |   +- CedulaInfo (NEW)  |
|  +- signals.py (NEW)      |
|  +- tasks.py (NEW)        |
|  +- scrapers.py (NEW)     |
|  +- views.py              |
|  |   +- refresh_cedula    |
|  +- apps.py               |
|  |   +- ready() imports   |
|  +- urls.py               |
|       +- /actualizar-...  |
+------------+--------------+
             |
             | post_save signal
             | async_task()
             v
+---------------------------+
|   Django-Q2 ORM Broker    |
|---------------------------|
|  django_q_ormq (tasks)    |
|  django_q_task (results)  |
+------------+--------------+
             |
             | polled by worker
             v
+---------------------------+
|   qcluster Worker Process |
|---------------------------|
|  Spawns workers (2)       |
|  Executes tasks           |
|  Monitors timeouts        |
+------------+--------------+
             |
             | runs scraper
             v
+---------------------------+
|   Playwright Browser      |
|---------------------------|
|  Chromium (headless)      |
|  Per-task instance        |
|  Scrapes Registraduria    |
+---------------------------+
```

## Anti-Patterns to Avoid

### 1. Sharing Playwright Browser Across Tasks
**Problem:** Playwright instances are not thread-safe. Attempting to reuse a browser across workers causes greenlet exceptions.

**Solution:** Create fresh `sync_playwright()` context within each task function.

### 2. Passing Model Instances to async_task
**Problem:** Django model instances cannot be serialized properly across process boundaries. The task receives stale data.

**Solution:** Pass `user.id` and re-fetch in task: `CustomUser.objects.get(id=user_id)`.

### 3. SQLite Lock Contention with Many Workers
**Problem:** SQLite has limited concurrent write support. Many workers hitting ORM broker simultaneously causes "database is locked" errors.

**Solution:** Keep `workers` low (2-4) and consider PostgreSQL for production scale.

### 4. Blocking Signal Handlers
**Problem:** If signal handler does heavy work, registration response is delayed.

**Solution:** Signal handler only calls `async_task()` (fast), actual work happens in worker.

### 5. Missing Playwright Browser Installation
**Problem:** `playwright install chromium` must run separately after pip install.

**Solution:** Add to deployment scripts/documentation. Error is clear but easy to miss.

## Sources

### Official Documentation (HIGH confidence)
- [Django-Q2 Configuration](https://django-q2.readthedocs.io/en/master/configure.html)
- [Django-Q2 Brokers](https://django-q2.readthedocs.io/en/master/brokers.html)
- [Django-Q2 Tasks API](https://django-q2.readthedocs.io/en/master/tasks.html)
- [Django Signals Documentation](https://docs.djangoproject.com/en/5.1/topics/signals/)
- [Playwright Python Getting Started](https://playwright.dev/python/docs/library)
- [Playwright GitHub - Background Task Issue #1207](https://github.com/microsoft/playwright-python/issues/1207)

### Secondary Sources (MEDIUM confidence)
- [Django-Q Examples](https://django-q.readthedocs.io/en/latest/examples.html)
- [AppConfig ready() Signal Pattern](https://gist.github.com/kylefox/177091bd8e4d88ac0cc19496064fd7d3)
- [Registraduria Certificate Service](https://wsp.registraduria.gov.co/certificado/)

---

*Architecture research: 2026-01-19*
