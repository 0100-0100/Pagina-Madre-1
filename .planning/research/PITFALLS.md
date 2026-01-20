# Pitfalls Research: v1.3 Async Background Jobs

**Domain:** Adding background task processing and web scraping to Django auth portal
**Researched:** 2026-01-19
**Target:** https://consultacenso.registraduria.gov.co/consultar/
**Overall Confidence:** HIGH (verified via Context7, official docs, and multiple sources)

---

## Web Scraping Pitfalls

### Critical: F5 CSPM Bot Detection

**What goes wrong:** The target Registraduria site uses F5 Client-Side Performance Monitoring (CSPM), which is JavaScript-based and collects browser telemetry. Standard HTTP requests (requests library) will be instantly blocked because they cannot execute JavaScript or generate the required `f5avr*_cspm_` cookies.

**Why it happens:** F5 CSPM requires:
1. Full JavaScript execution to generate telemetry
2. Browser fingerprint consistency
3. Behavioral patterns matching human interaction
4. Session persistence via TS* cookies

**Warning signs:**
- HTTP 403 responses
- Empty responses with JavaScript redirect
- CAPTCHAs appearing (not present initially but may trigger)
- Response containing only `<noscript>` fallback message

**Consequences:** Scraping fails completely; IP may be temporarily blocked.

**Prevention strategy:**
1. Use Playwright (not requests) with stealth plugins
2. Install `playwright-stealth` or `patchright` for detection evasion
3. Use `headless=False` initially for debugging, then test `headless=True`
4. Implement realistic delays between actions (2-5 seconds)
5. Consider residential proxy if datacenter IPs get blocked

**Detection:** Test with simple Playwright script first; if page returns "Se requiere JavaScript" warning or blocks, stealth measures are insufficient.

**Phase to address:** Phase 1 (Scraping Infrastructure)

**Sources:**
- [F5 Bypass Proxy Guide for Web Scraping 2025](https://medium.com/@datajournal/f5-bypass-proxy-for-web-scraping-a-complete-guide-da9dc1638a0a)
- [Scrapfly F5 Bypass Documentation](https://scrapfly.io/bypass/f5)

---

### Critical: Playwright Detection via CDP

**What goes wrong:** Modern anti-bot systems detect Playwright through Chrome DevTools Protocol (CDP) commands. Even with stealth plugins, CDP-based detection can identify automated browsers.

**Why it happens:** Anti-bot systems have evolved to detect:
- `navigator.webdriver = true` flag
- HeadlessChrome user agent
- CDP command patterns
- Missing browser features/plugins

**Warning signs:**
- Detection on sites like BrowserScan or CreepJS
- Inconsistent success rates (works sometimes, fails others)
- Behavioral analysis triggering after initial success

**Consequences:** Initial success followed by blocks; inconsistent scraping reliability.

**Prevention strategy:**
```python
# Use stealth plugin
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async with async_playwright() as p:
    browser = await p.chromium.launch(headless=False)
    context = await Stealth().apply(browser.new_context())
    page = await context.new_page()
```

Alternative: Use `patchright` (currently considered most undetectable):
```bash
pip install patchright
patchright install chrome
```

**Detection:** Test against [BrowserScan](https://www.browserscan.net/) or [CreepJS](https://abrahamjuliot.github.io/creepjs/) before targeting production site.

**Phase to address:** Phase 1 (Scraping Infrastructure)

**Sources:**
- [Patchright GitHub - Undetected Playwright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python)
- [From Puppeteer Stealth to Nodriver Evolution](https://blog.castle.io/from-puppeteer-stealth-to-nodriver-how-anti-detect-frameworks-evolved-to-evade-bot-detection/)

---

### Moderate: Playwright Memory Leaks in Long-Running Applications

**What goes wrong:** Keeping browser contexts open for extended periods causes memory growth. Request/response objects accumulate and are only flushed when creating new contexts.

**Why it happens:** Playwright stores HTTP response data in memory. Frequent requests (e.g., polling) can consume 1GB+ within an hour.

**Warning signs:**
- Worker process memory growing over time
- Django-Q worker crashes with "JavaScript heap out of memory"
- Slower scraping performance over time

**Consequences:** Worker crashes; server memory exhaustion; unreliable background jobs.

**Prevention strategy:**
1. Create new browser context for each scraping task
2. Close context and page explicitly after each task
3. Do NOT reuse contexts across multiple scrapes
4. Set task timeout in Django-Q2 to prevent runaway tasks

```python
async def scrape_cedula(cedula: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()  # Fresh context
        try:
            page = await context.new_page()
            # ... scraping logic ...
            return result
        finally:
            await context.close()  # Always close
            await browser.close()
```

**Detection:** Monitor worker process memory via `htop` or process monitoring.

**Phase to address:** Phase 2 (Task Integration)

**Sources:**
- [Playwright Memory Issue #6319](https://github.com/microsoft/playwright/issues/6319)
- [Playwright Memory Leak Issue #15400](https://github.com/microsoft/playwright/issues/15400)

---

### Moderate: Rate Limiting and IP Blocking

**What goes wrong:** Scraping too fast triggers rate limiting or IP blocks. Government sites may have aggressive rate limits to prevent abuse.

**Why it happens:** F5 monitors request frequency per IP. Exceeding thresholds triggers temporary or permanent blocks.

**Warning signs:**
- HTTP 429 (Too Many Requests) responses
- HTTP 503 (Service Unavailable) responses
- Increasing failure rates over time
- Different results from different IPs

**Consequences:** Temporary scraping outage; need to wait for block to lift; possible permanent IP blacklist.

**Prevention strategy:**
1. Implement exponential backoff with jitter:
```python
import random
import asyncio

async def backoff_delay(attempt: int, base: float = 2.0, max_delay: float = 60.0):
    delay = min(base ** attempt + random.uniform(0, 1), max_delay)
    await asyncio.sleep(delay)
```

2. Add minimum delay between requests (3-5 seconds for government sites)
3. Honor `Retry-After` header if present
4. Implement circuit breaker pattern for repeated failures
5. Consider scraping during off-peak hours (late night Colombia time)

**Detection:** Track success/failure rates per hour; alert on failure rate exceeding 20%.

**Phase to address:** Phase 2 (Error Handling)

**Sources:**
- [Exponential Backoff for Rate Limiting](https://substack.thewebscraping.club/p/rate-limit-scraping-exponential-backoff)
- [ScraperAPI Best Practices 2025](https://www.scraperapi.com/web-scraping/best-practices/)

---

## Django-Q2 Pitfalls

### Critical: SQLite Database Locking

**What goes wrong:** SQLite's default rollback journal mode causes "database is locked" errors when Django-Q2 workers try to read/write simultaneously with the main Django application.

**Why it happens:** SQLite's default mode blocks ALL reads during writes. With background workers polling for tasks + main app serving requests, lock contention is inevitable.

**Warning signs:**
- `django.db.utils.OperationalError: database is locked`
- Intermittent 500 errors during task execution
- Tasks stuck in "queued" state

**Consequences:** Failed tasks; user-facing errors; data corruption risk if transactions don't complete properly.

**Prevention strategy:**

1. **Enable WAL mode** (Write-Ahead Logging) - ESSENTIAL for SQLite + Django-Q2:
```python
# settings.py or a migration
from django.db.backends.signals import connection_created

def enable_wal_mode(sender, connection, **kwargs):
    if connection.vendor == 'sqlite':
        cursor = connection.cursor()
        cursor.execute('PRAGMA journal_mode=wal;')
        cursor.execute('PRAGMA busy_timeout=5000;')  # 5 second timeout
        cursor.execute('PRAGMA synchronous=NORMAL;')

connection_created.connect(enable_wal_mode)
```

2. **Limit workers to 1** for SQLite:
```python
Q_CLUSTER = {
    'name': 'DjangORM',
    'workers': 1,  # Critical for SQLite
    'timeout': 120,
    'retry': 180,
    'orm': 'default'
}
```

3. **Increase busy timeout** in Django settings (Django 5.1+):
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'init_command': "PRAGMA journal_mode=wal; PRAGMA busy_timeout=5000;",
        }
    }
}
```

**Detection:** Log "database is locked" errors; they indicate locking issues even if retries succeed.

**Phase to address:** Phase 1 (Django-Q2 Setup)

**Sources:**
- [Django SQLite Locked Error Blog](https://blog.pecar.me/django-sqlite-dblock)
- [Django-Q SQLite Locking Issue #617](https://github.com/Koed00/django-q/issues/617)
- [Enabling WAL in SQLite in Django](https://djangoandy.com/2024/07/08/enabling-wal-in-sqlite-in-django/)

---

### Critical: Retry Timing Misconfiguration

**What goes wrong:** If `retry` value is less than task execution time, Django-Q2 re-queues tasks before they complete, causing duplicate executions.

**Why it happens:** Django-Q2's retry mechanism re-presents tasks if the broker doesn't receive completion acknowledgment within the retry window. Long-running scraping tasks easily exceed default timeouts.

**Warning signs:**
- Same cedula being scraped multiple times
- Task count growing unexpectedly
- "Duplicate" results in database

**Consequences:** Wasted resources; potential data inconsistency; rate limiting triggered faster.

**Prevention strategy:**
```python
Q_CLUSTER = {
    'name': 'DjangORM',
    'workers': 1,
    'timeout': 120,      # Max 2 minutes per task
    'retry': 180,        # Re-queue after 3 minutes (MUST be > timeout)
    'max_attempts': 3,   # Limit retries
    'ack_failures': True,  # Don't retry failed tasks infinitely
    'orm': 'default'
}
```

**Rule:** `retry` MUST be greater than `timeout`, and both MUST be greater than your longest expected task duration.

**Detection:** Monitor task queue for duplicate task IDs; log task start/end times.

**Phase to address:** Phase 1 (Django-Q2 Setup)

**Sources:**
- [Django-Q2 Configuration Docs](https://django-q2.readthedocs.io/en/latest/configure.html)
- [Django-Q Retry Issue #495](https://github.com/Koed00/django-q/issues/495)

---

### Moderate: Worker Not Starting or Silently Dying

**What goes wrong:** Django-Q2 cluster doesn't start, or starts but workers die silently without processing tasks.

**Why it happens:** Multiple causes:
- Missing `qcluster` management command execution
- Incorrect broker configuration
- Worker process crashes without logging

**Warning signs:**
- Tasks remain in "queued" state indefinitely
- No worker processes visible in `ps aux | grep qcluster`
- No log output from Django-Q2

**Consequences:** Background tasks never execute; users see stale data.

**Prevention strategy:**
1. Run qcluster explicitly: `python manage.py qcluster`
2. Add comprehensive logging:
```python
Q_CLUSTER = {
    'name': 'DjangORM',
    'workers': 1,
    'orm': 'default',
    'log_level': 'DEBUG',  # Enable verbose logging initially
}
```
3. Use process supervisor (systemd, supervisor) for production
4. Monitor with Django-Q2 admin panel

**Detection:** Check `/admin/django_q/` for task status; verify qcluster process is running.

**Phase to address:** Phase 1 (Django-Q2 Setup)

**Sources:**
- [Django-Q2 Documentation](https://django-q2.readthedocs.io/en/latest/)

---

## Integration Pitfalls

### Critical: Signal-to-Task Race Condition

**What goes wrong:** `post_save` signal triggers background task, but task starts before database transaction commits. Task queries database and finds no record.

**Why it happens:** Django signals fire synchronously within the request. If using `ATOMIC_REQUESTS` or explicit transactions, the task may query the database before the transaction commits.

**Warning signs:**
- `DoesNotExist` errors in task logs
- "Referral not found" errors immediately after creation
- Intermittent failures (race condition timing-dependent)

**Consequences:** Failed tasks; missing data; user confusion when scraping "doesn't work."

**Prevention strategy:**

Use `transaction.on_commit()` to delay task dispatch:
```python
from django.db import transaction
from django_q.tasks import async_task

def create_referral(request):
    with transaction.atomic():
        referral = Referral.objects.create(
            cedula=cedula,
            referred_by=request.user
        )
        # Dispatch AFTER commit
        transaction.on_commit(
            lambda: async_task('apps.referrals.tasks.verify_cedula', referral.id)
        )
    return redirect('home')
```

Or use a signal with on_commit:
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

@receiver(post_save, sender=Referral)
def trigger_verification(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(
            lambda: async_task('verify_cedula', instance.id)
        )
```

**Detection:** Log task dispatch time vs. task execution time; check for DoesNotExist errors.

**Phase to address:** Phase 2 (Signal Integration)

**Sources:**
- [Django Async Job Database Integration](https://spapas.github.io/2019/02/25/django-fix-async-db/)
- [Celery Database Transactions TestDriven.io](https://testdriven.io/blog/celery-database-transactions/)
- [Django Race Condition on_commit](https://dev.to/k4ml/django-fixing-race-condition-when-queuing-with-oncommit-hook-7ae)

---

### Moderate: Signals Not Being Synchronous Misconception

**What goes wrong:** Developers assume Django signals are asynchronous (like JavaScript events) and put blocking operations in signal handlers, causing slow request times.

**Why it happens:** The event-driven pattern looks async but signals execute synchronously in the same thread as the caller.

**Warning signs:**
- Slow page loads after form submissions
- Timeout errors during user registration
- Signal handlers doing network calls directly

**Consequences:** Poor user experience; timeout errors; cascading failures.

**Prevention strategy:**
1. Signal handlers should ONLY dispatch to background tasks
2. Never make HTTP requests, database-heavy queries, or scraping calls in signal handlers
3. Keep signal handlers under 100ms

```python
# BAD - blocks request
@receiver(post_save, sender=Referral)
def verify_immediately(sender, instance, created, **kwargs):
    if created:
        result = scrape_registraduria(instance.cedula)  # Blocks for 30+ seconds!
        instance.verified = result['valid']
        instance.save()

# GOOD - dispatches to background
@receiver(post_save, sender=Referral)
def queue_verification(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(
            lambda: async_task('verify_cedula', instance.id)
        )  # Returns instantly
```

**Detection:** Profile request times; signals taking >100ms indicate blocking operations.

**Phase to address:** Phase 2 (Signal Integration)

**Sources:**
- [Django Signals Sync/Async Explanation](https://www.mattlayman.com/blog/2023/django-signals-async/)
- [Django Anti-Patterns: Signals](https://lincolnloop.com/blog/django-anti-patterns-signals/)

---

### Moderate: Testing Difficulty with on_commit

**What goes wrong:** Tests using `TestCase` wrap everything in a transaction that rolls back, so `on_commit` callbacks never execute.

**Why it happens:** Django's `TestCase` intentionally uses transactions for test isolation. Since transactions never commit, `on_commit` never fires.

**Warning signs:**
- Tests pass but production fails
- Background tasks never triggered in tests
- Mocking doesn't catch task dispatch

**Consequences:** False confidence from passing tests; bugs discovered only in production.

**Prevention strategy:**
1. Use `TransactionTestCase` for integration tests involving background tasks
2. Use `django.test.utils.CaptureOnCommitCallbacks` (Django 3.2+):
```python
from django.test import TestCase
from django.test.utils import CaptureOnCommitCallbacks

class ReferralTestCase(TestCase):
    def test_verification_queued(self):
        with CaptureOnCommitCallbacks(execute=True) as callbacks:
            referral = Referral.objects.create(cedula='12345')
        # Callbacks were captured and executed
        self.assertEqual(len(callbacks), 1)
```
3. Mock `async_task` at import level for unit tests

**Detection:** Add integration test that verifies task was actually queued.

**Phase to address:** Phase 3 (Testing)

**Sources:**
- [Django Database Transactions Documentation](https://docs.djangoproject.com/en/6.0/topics/db/transactions/)

---

### Minor: Forgetting to Disconnect Test Signals

**What goes wrong:** Signal handlers registered in tests persist across test methods, causing unexpected behavior or duplicated task dispatches.

**Why it happens:** Signal connections are global; `@receiver` decorator connects permanently.

**Warning signs:**
- Tests interfering with each other
- "Multiple tasks queued" when expecting one
- Flaky tests that pass/fail randomly

**Prevention strategy:**
```python
from django.test import TestCase
from django.db.models.signals import post_save

class ReferralTestCase(TestCase):
    def setUp(self):
        # Disconnect during tests if needed
        post_save.disconnect(trigger_verification, sender=Referral)

    def tearDown(self):
        # Reconnect after
        post_save.connect(trigger_verification, sender=Referral)
```

**Phase to address:** Phase 3 (Testing)

---

## Error Handling Pitfalls

### Critical: Silent Task Failures

**What goes wrong:** Scraping tasks fail but no one notices. Users see "pending" verification status indefinitely.

**Why it happens:** Django-Q2 logs failures but doesn't notify anyone. Without monitoring, failures accumulate silently.

**Warning signs:**
- Growing number of "pending" referrals
- Task failure count increasing in admin
- User complaints about verification not completing

**Consequences:** Bad user experience; lost trust; manual cleanup required.

**Prevention strategy:**
1. Configure error reporting:
```python
Q_CLUSTER = {
    'name': 'DjangORM',
    'error_reporter': {
        'sentry': {
            'dsn': 'YOUR_SENTRY_DSN'
        }
    }
}
```

2. Implement failure callback in tasks:
```python
from django_q.tasks import async_task

def on_task_failure(task):
    # Update referral status to 'failed'
    # Send notification
    pass

async_task(
    'verify_cedula',
    referral_id,
    hook='apps.referrals.tasks.on_task_failure'
)
```

3. Add periodic job to check for stuck "pending" referrals

**Detection:** Dashboard showing pending vs. verified ratio; alert if pending > threshold.

**Phase to address:** Phase 2 (Error Handling)

**Sources:**
- [Django-Q2 Error Reporter Configuration](https://django-q2.readthedocs.io/en/latest/configure.html)

---

### Moderate: Not Distinguishing Error Types

**What goes wrong:** All scraping failures treated the same. Network timeout retried same as "cedula not found" (which should not retry).

**Why it happens:** Generic exception handling without categorization.

**Warning signs:**
- Retrying tasks that will never succeed
- Valid "not found" results causing error alerts
- Wasted retries on permanent failures

**Consequences:** Resource waste; misleading error metrics; user confusion.

**Prevention strategy:**
```python
class ScrapingError(Exception):
    """Base class for scraping errors"""
    pass

class NetworkError(ScrapingError):
    """Retry-able: network issues"""
    pass

class RateLimitError(ScrapingError):
    """Retry-able: rate limited, back off"""
    pass

class CedulaNotFoundError(ScrapingError):
    """NOT retry-able: cedula genuinely not found"""
    pass

class BotDetectedError(ScrapingError):
    """NOT retry-able: need to change approach"""
    pass

def verify_cedula(referral_id):
    try:
        result = scrape_registraduria(cedula)
    except NetworkError:
        raise  # Django-Q2 will retry
    except RateLimitError as e:
        raise  # Retry after backoff
    except CedulaNotFoundError:
        referral.status = 'not_found'
        referral.save()
        return  # Don't retry
    except BotDetectedError:
        referral.status = 'blocked'
        referral.save()
        # Alert immediately
        return
```

**Phase to address:** Phase 2 (Error Handling)

---

## Prevention Summary

| Pitfall | Severity | Phase | Quick Fix |
|---------|----------|-------|-----------|
| F5 CSPM bot detection | Critical | 1 | Use Playwright + stealth plugin |
| CDP detection | Critical | 1 | Use patchright or undetected-playwright |
| SQLite locking | Critical | 1 | Enable WAL mode, limit workers to 1 |
| Retry timing | Critical | 1 | Set retry > timeout > max task duration |
| Signal race condition | Critical | 2 | Use transaction.on_commit() |
| Silent task failures | Critical | 2 | Configure error reporter + monitoring |
| Memory leaks | Moderate | 2 | Create fresh context per task |
| Rate limiting | Moderate | 2 | Exponential backoff + jitter |
| Signals blocking | Moderate | 2 | Only dispatch to tasks, never block |
| Error categorization | Moderate | 2 | Custom exception hierarchy |
| Testing on_commit | Moderate | 3 | Use CaptureOnCommitCallbacks |
| Worker not starting | Moderate | 1 | Add logging, use process supervisor |

---

## Phase-Specific Risk Assessment

| Phase | Risk Level | Primary Pitfalls | Mitigation |
|-------|------------|------------------|------------|
| Phase 1: Scraping Infrastructure | HIGH | Bot detection, SQLite locking | Test stealth thoroughly; enable WAL |
| Phase 2: Task Integration | MEDIUM | Race conditions, silent failures | Use on_commit; add monitoring |
| Phase 3: Error Handling | LOW | Standard patterns | Follow exception hierarchy |
| Phase 4: UI/UX | LOW | None specific | Standard Django patterns |

---

## Sources

### Bot Detection and Evasion
- [Scrapfly F5 Bypass](https://scrapfly.io/bypass/f5)
- [F5 Bypass Proxy Guide 2025](https://medium.com/@datajournal/f5-bypass-proxy-for-web-scraping-a-complete-guide-da9dc1638a0a)
- [Patchright GitHub](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python)
- [Anti-Detect Framework Evolution](https://blog.castle.io/from-puppeteer-stealth-to-nodriver-how-anti-detect-frameworks-evolved-to-evade-bot-detection/)
- [Playwright Stealth PyPI](https://pypi.org/project/playwright-stealth/)

### Django-Q2 and SQLite
- [Django-Q2 Configuration Documentation](https://django-q2.readthedocs.io/en/latest/configure.html)
- [Django SQLite Locked Error](https://blog.pecar.me/django-sqlite-dblock)
- [Django-Q SQLite Issue #617](https://github.com/Koed00/django-q/issues/617)
- [Enabling WAL in Django](https://djangoandy.com/2024/07/08/enabling-wal-in-sqlite-in-django/)
- [SQLite WAL Documentation](https://sqlite.org/wal.html)

### Signal and Transaction Patterns
- [Django Async Job Database Fix](https://spapas.github.io/2019/02/25/django-fix-async-db/)
- [Celery Database Transactions](https://testdriven.io/blog/celery-database-transactions/)
- [Django Signals Anti-Patterns](https://lincolnloop.com/blog/django-anti-patterns-signals/)
- [Django Signals Sync/Async](https://www.mattlayman.com/blog/2023/django-signals-async/)
- [Race Condition with on_commit](https://dev.to/k4ml/django-fixing-race-condition-when-queuing-with-oncommit-hook-7ae)

### Rate Limiting and Backoff
- [Exponential Backoff for Scraping](https://substack.thewebscraping.club/p/rate-limit-scraping-exponential-backoff)
- [ScraperAPI Best Practices 2025](https://www.scraperapi.com/web-scraping/best-practices/)

### Memory and Performance
- [Playwright Memory Issue #6319](https://github.com/microsoft/playwright/issues/6319)
- [Playwright Memory Leak #15400](https://github.com/microsoft/playwright/issues/15400)
