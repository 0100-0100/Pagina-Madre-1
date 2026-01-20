# Stack Research: v1.3 Async Background Jobs

**Project:** Pagina-Madre (Django Auth Portal)
**Researched:** 2026-01-19
**Overall confidence:** HIGH

## Executive Summary

For adding async background jobs and Playwright web scraping to the existing Django 4.2 + SQLite stack, the recommended additions are **Django-Q2** (v1.9.0) with ORM broker and **Playwright** (v1.57.0) with **playwright-stealth** (v2.0.1). This combination provides:

1. SQLite-compatible task queue (no Redis required)
2. Headless browser automation for JavaScript-rendered pages
3. Basic bot evasion for Registraduria's F5 protection
4. Clean integration with existing Django architecture

**Critical insight:** Django-Q2 uses multiprocessing (separate worker processes), which avoids the "event loop already running" issue that plagues other async integrations. Each worker process can safely initialize its own Playwright instance.

---

## Recommended Stack Additions

### Core Packages

| Package | Version | Purpose | Why This |
|---------|---------|---------|----------|
| `django-q2` | 1.9.0 | Background task queue | Only Django-native queue that works with SQLite via ORM broker. Actively maintained fork of Django-Q. Multiprocessing architecture. |
| `playwright` | 1.57.0 | Headless browser automation | Official Microsoft library. Handles JavaScript-rendered pages. Required for scraping Registraduria census. |
| `playwright-stealth` | 2.0.1 | Basic bot evasion | Patches Playwright to hide automation signals. Helps with F5 bot protection. |

### Automatic Dependencies (installed with above)

| Package | Version | Installed By | Purpose |
|---------|---------|--------------|---------|
| `django-picklefield` | 3.4.0 | django-q2 | Serializes task arguments to database |

### Browser Binary (required, not a pip package)

After installing playwright, run:
```bash
playwright install chromium
```

This downloads the Chromium browser binary (~150MB). Only Chromium needed - Firefox/WebKit unnecessary for this use case.

---

## Installation Commands

```bash
# Activate virtual environment first
source .venv/bin/activate

# Install Python packages
pip install django-q2==1.9.0 playwright==1.57.0 playwright-stealth==2.0.1

# Install Chromium browser binary
playwright install chromium

# Update requirements.txt
pip freeze > requirements.txt
```

### Updated requirements.txt

```
Django>=4.2,<5.0
python-decouple>=3.8
django-q2==1.9.0
playwright==1.57.0
playwright-stealth==2.0.1
```

---

## Django-Q2 Configuration

### SQLite-Specific Setup (ORM Broker)

Add to `settings.py`:

```python
# Django-Q2 Configuration
Q_CLUSTER = {
    'name': 'PaginaMadre',
    'workers': 2,              # Low for SQLite (avoid lock contention)
    'timeout': 120,            # 2 minutes per task (Playwright can be slow)
    'retry': 180,              # Retry after 3 minutes if not acknowledged
    'queue_limit': 10,         # Small queue for SQLite
    'bulk': 1,                 # Process one at a time (SQLite safety)
    'orm': 'default',          # Use Django's default database
    'poll': 1.0,               # Check queue every second
    'save_limit': 100,         # Keep last 100 completed tasks
    'ack_failures': True,      # Acknowledge failed tasks (prevent retry loops)
    'max_attempts': 3,         # Retry failed tasks up to 3 times
    'catch_up': False,         # Don't run missed schedules (avoid backlog)
}
```

### Add to INSTALLED_APPS

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'django_q',
]
```

### Run Migrations

```bash
python manage.py migrate django_q
```

This creates these tables:
- `django_q_ormq` - Task queue
- `django_q_task` - Task results
- `django_q_schedule` - Scheduled tasks

### Running the Worker Cluster

```bash
# Development (foreground, with output)
python manage.py qcluster

# Production (use supervisor, systemd, or similar)
```

**Important:** The qcluster command must be running for tasks to process. In development, run it in a separate terminal.

---

## Playwright Setup

### Sync API Usage Pattern (Django-Q2 Compatible)

Since Django-Q2 workers are separate processes, use the sync API directly:

```python
# scraper.py - Example task
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def scrape_cedula(cedula: str) -> dict:
    """
    Scrape Registraduria census for cedula.
    Called as Django-Q2 task in separate worker process.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Apply stealth to avoid bot detection
        stealth = Stealth()
        context = browser.new_context()
        stealth.apply_stealth_sync(context)

        page = context.new_page()

        try:
            # Navigate and scrape
            page.goto("https://wsp.registraduria.gov.co/censo/consultar/")
            # ... form interaction and data extraction ...

            return {
                'status': 'success',
                'data': {...}
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
        finally:
            browser.close()
```

### Queueing Tasks

```python
# views.py or signals.py
from django_q.tasks import async_task

def on_user_registration(user):
    """Queue cedula validation after registration."""
    async_task(
        'apps.scraper.scrape_cedula',  # Task function path
        user.cedula,                    # Positional argument
        hook='apps.scraper.save_result',  # Callback when done
        timeout=120,                    # 2 minute timeout
    )
```

### Stealth Configuration

```python
from playwright_stealth import Stealth, ALL_EVASIONS_DISABLED_KWARGS

# Default stealth (all evasions enabled)
stealth = Stealth()

# Or customize which evasions to use
stealth = Stealth(
    navigator_webdriver=True,      # Hide webdriver flag
    navigator_plugins=True,        # Fake plugins
    navigator_languages=True,      # Realistic languages
    webgl_vendor=True,             # Fake WebGL vendor
    # ... etc
)

# Apply to browser context
stealth.apply_stealth_sync(context)
```

---

## Integration Notes

### How These Integrate with Existing Django App

1. **Database**: Django-Q2 uses the same SQLite database via ORM broker. No additional database needed.

2. **Settings**: Only `Q_CLUSTER` config and `django_q` in INSTALLED_APPS needed.

3. **Migrations**: Single migrate command adds Django-Q2 tables.

4. **Admin**: Django-Q2 automatically adds task management to Django Admin (Queued Tasks, Successful Tasks, Failed Tasks, Scheduled Tasks).

5. **Signals**: Can trigger tasks on model save via Django signals (e.g., post_save on User model).

6. **Views**: Can trigger tasks from views (e.g., manual refresh button).

### Architecture Pattern

```
[User Registration]
    -> [Django View]
    -> [async_task()] queues to ORM
    -> [qcluster worker] picks up task
    -> [Playwright scrapes] Registraduria
    -> [Hook saves result] to CedulaInfo model
```

### SQLite Considerations

- **Workers**: Keep at 2 or fewer to avoid SQLite lock contention
- **Bulk**: Set to 1 (process one task at a time)
- **Poll**: 1.0 second is fine (not high traffic)
- **WAL mode**: Consider enabling for better concurrency:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,  # Wait 20 seconds on lock
        },
    }
}
```

### Bot Protection Strategy

Registraduria uses F5 bot protection. playwright-stealth provides basic evasion but may not bypass all protections. Strategy:

1. **Start with stealth**: May work for simple bot detection
2. **Add delays**: Human-like timing between actions
3. **Handle failures**: Store error states, allow manual retry
4. **Monitor**: If blocked frequently, consider Camoufox upgrade

---

## What NOT to Add

### Packages to Avoid

| Package | Why NOT |
|---------|---------|
| `celery` | Requires Redis or RabbitMQ. Overkill for this scale. Complex setup. |
| `redis` / `django-redis` | SQLite-only requirement. Adding Redis adds infrastructure. |
| `huey` | Less Django-native than Django-Q2. Less admin integration. |
| `selenium` | Older, slower than Playwright. Worse async support. |
| `beautifulsoup4` | Not needed - Registraduria page is JS-rendered, need real browser. |
| `requests` | Can't execute JavaScript. Won't work for this target. |
| `camoufox` | More complex setup. Only add if playwright-stealth fails. |
| `nest_asyncio` | Not needed - Django-Q2 multiprocessing avoids event loop conflicts. |
| `undetected-playwright` | Unmaintained. playwright-stealth is the maintained option. |

### Approaches to Avoid

| Approach | Why NOT |
|----------|---------|
| Running Playwright in Django request cycle | Blocks web server. Playwright operations take 5-30 seconds. |
| Sharing Playwright instance across workers | Each worker needs its own instance due to multiprocessing. |
| Using async API with sync Django | Event loop conflicts. Stick with sync_api in workers. |
| Redis just for Django-Q2 | Unnecessary complexity. ORM broker is fine for this scale. |
| Multiple browser types | Only Chromium needed. Firefox/WebKit add download time. |

---

## Version Compatibility Matrix

| Component | Installed | Requires | Status |
|-----------|-----------|----------|--------|
| Python | 3.14 | 3.9-3.13 (Q2), 3.9+ (Playwright) | CHECK: django-picklefield 3.4.0 requires 3.10+ |
| Django | 4.2 | 4.2-6.0 (Q2), any (Playwright) | OK |
| SQLite | bundled | any (via Django ORM) | OK |
| OS | macOS/Linux | macOS, Linux, Windows | OK |

### Python 3.14 Note

Django-Q2 officially supports up to Python 3.13. Python 3.14 may work but is not officially tested. Monitor for issues. Consider testing with 3.13 if problems arise.

django-picklefield 3.4.0 lists Python 3.14 support explicitly.

---

## Sources

### Official Documentation (HIGH confidence)
- [Django-Q2 Configuration](https://django-q2.readthedocs.io/en/master/configure.html)
- [Django-Q2 Brokers](https://django-q2.readthedocs.io/en/master/brokers.html)
- [Django-Q2 Tasks](https://django-q2.readthedocs.io/en/master/tasks.html)
- [Playwright Python Installation](https://playwright.dev/python/docs/intro)
- [Playwright Python Library API](https://playwright.dev/python/docs/library)

### PyPI (HIGH confidence - version info)
- [django-q2 1.9.0](https://pypi.org/project/django-q2/)
- [playwright 1.57.0](https://pypi.org/project/playwright/)
- [playwright-stealth 2.0.1](https://pypi.org/project/playwright-stealth/)
- [django-picklefield 3.4.0](https://pypi.org/project/django-picklefield/)

### GitHub (HIGH confidence)
- [Django-Q2 Repository](https://github.com/django-q2/django-q2)
- [Playwright Python Issues - Multiprocessing](https://github.com/microsoft/playwright-python/issues/937)
- [Playwright Python Issues - Celery Workers](https://github.com/microsoft/playwright-python/issues/1995)

### Community Research (MEDIUM confidence)
- [ZenRows - Playwright Cloudflare Bypass](https://www.zenrows.com/blog/playwright-cloudflare-bypass)
- [BrightData - Playwright Stealth](https://brightdata.com/blog/how-tos/avoid-bot-detection-with-playwright-stealth)
- [DEV.to - Playwright Flask Async Conflict](https://dev.to/deepak_mishra_35863517037/integrating-playwright-with-flask-resolving-the-async-conflict-2d9o)

---

## Confidence Assessment

| Area | Level | Reason |
|------|-------|--------|
| Django-Q2 version/config | HIGH | Verified via official docs and PyPI |
| ORM broker for SQLite | HIGH | Documented feature with examples |
| Playwright version/usage | HIGH | Verified via official docs and PyPI |
| playwright-stealth integration | MEDIUM | Third-party package, verified on PyPI |
| F5 bypass effectiveness | LOW | Depends on target site's specific protection |
| Python 3.14 compatibility | MEDIUM | django-picklefield supports it, Q2 untested |

---

## Open Questions for Phase Planning

1. **Bot detection severity**: How aggressive is Registraduria's F5 protection? May need to upgrade to Camoufox if playwright-stealth insufficient.

2. **Rate limiting**: What's the appropriate delay between scraping requests? May need to implement backoff.

3. **Error handling**: What specific error states does Registraduria return? Need to map to CedulaInfo status field.

4. **Browser binary deployment**: How to handle Playwright browser binary in production? May need dockerfile or install script.
