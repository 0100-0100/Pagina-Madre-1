# Research Summary: v1.3 Async Background Jobs

**Project:** Pagina-Madre (Django Authentication Portal)
**Milestone:** v1.3 Async Background Jobs
**Research Date:** 2026-01-19
**Confidence:** HIGH

## Executive Summary

Adding background task processing with web scraping to this Django 4.2 + SQLite auth portal requires careful integration of Django-Q2 (task queue), Playwright (headless browser), and proper anti-bot evasion for the Registraduria's F5-protected census page. The recommended approach is conservative: single worker, WAL mode for SQLite, fresh browser instances per task, and `transaction.on_commit()` for signal-triggered tasks.

The highest risk is **F5 CSPM bot detection**. Standard Playwright will be blocked; `playwright-stealth` provides baseline evasion but success is not guaranteed. Build the system to handle failures gracefully rather than attempting to defeat all bot detection. The second major risk is **SQLite database locking** which requires enabling WAL mode and limiting Django-Q2 to a single worker.

Django-Q2's multiprocessing architecture is ideal here because each worker process can safely initialize its own Playwright instance without async/event-loop conflicts. This is a well-documented integration pattern with high confidence.

## Stack Decision

**Final stack additions:**

| Package | Version | Purpose |
|---------|---------|---------|
| `django-q2` | 1.9.0 | Background task queue with ORM broker (SQLite compatible) |
| `playwright` | 1.57.0 | Headless browser automation for JS-rendered pages |
| `playwright-stealth` | 2.0.1 | Basic bot detection evasion |

**Post-install requirement:** `playwright install chromium` (~150MB browser binary)

**Configuration critical settings:**
- `Q_CLUSTER.workers = 1` (SQLite lock avoidance)
- `Q_CLUSTER.timeout = 120` (Playwright can be slow)
- `Q_CLUSTER.retry = 180` (must exceed timeout)
- `Q_CLUSTER.orm = 'default'` (use SQLite via Django ORM)

## Feature Requirements

### Must Have (Table Stakes)
- Task queue system (Django-Q2 with ORM broker)
- Headless browser scraping (Playwright + stealth)
- CedulaInfo model with all response states (pending, found, not_found, cancelled, error)
- Auto-trigger on user registration via post_save signal
- Manual refresh endpoint with rate limiting
- Retry logic with exponential backoff (max 3 attempts)
- Error handling for all Registraduria response types

### Should Have (v1.3 Scope)
- Task progress visibility (status field polling)
- Admin dashboard integration (Django-Q2 provides this)
- Raw response storage for debugging

### Defer to v2+
- Proxy rotation (only if consistently blocked)
- Scheduled re-validation (electoral data rarely changes)
- Batch processing (overkill for <100 users)
- WebSocket real-time updates (polling sufficient)

## Architecture Pattern

**Integration approach:** Signal-triggered background tasks with fresh browser instances per task.

```
User Registration -> post_save signal -> transaction.on_commit() -> async_task()
                                                                        |
qcluster worker <-- ORM broker polling <--------------------------------+
     |
     v
Playwright (fresh instance) -> scrape Registraduria -> update CedulaInfo
```

**New components in accounts app:**
1. `CedulaInfo` model (OneToOne to CustomUser)
2. `signals.py` (post_save handler with on_commit)
3. `tasks.py` (fetch_cedula_info orchestration)
4. `scrapers.py` (Playwright scraping logic)
5. One new view (manual refresh endpoint)

**Existing components modified:**
- `settings.py` (add django_q to INSTALLED_APPS, Q_CLUSTER config, WAL mode)
- `apps.py` (import signals in ready())
- `urls.py` (add refresh endpoint)
- `admin.py` (register CedulaInfo)

## Critical Pitfalls

### 1. F5 CSPM Bot Detection (CRITICAL)
**Prevention:** Use Playwright with `playwright-stealth`. Test against BrowserScan before production. Accept some failures - build graceful error handling rather than trying to defeat all detection.

### 2. SQLite Database Locking (CRITICAL)
**Prevention:** Enable WAL mode via connection signal. Limit workers to 1. Set busy_timeout to 5000ms.

```python
# settings.py
def enable_wal_mode(sender, connection, **kwargs):
    if connection.vendor == 'sqlite':
        cursor = connection.cursor()
        cursor.execute('PRAGMA journal_mode=wal;')
        cursor.execute('PRAGMA busy_timeout=5000;')
```

### 3. Signal-to-Task Race Condition (CRITICAL)
**Prevention:** Always use `transaction.on_commit()` when dispatching tasks from signals:
```python
transaction.on_commit(lambda: async_task('accounts.tasks.fetch_cedula_info', instance.id))
```

### 4. Retry Timing Misconfiguration (CRITICAL)
**Prevention:** Ensure `retry` > `timeout` > max task duration. Default: timeout=120, retry=180.

### 5. Playwright Memory Leaks (MODERATE)
**Prevention:** Create fresh browser context per task. Always close context and browser in finally block. Never share instances across tasks.

## Implications for Roadmap

### Phase 1: Django-Q2 Foundation
**Rationale:** Infrastructure must exist before building on it
**Delivers:** Working task queue, SQLite WAL mode, admin integration
**Implements:** Q_CLUSTER config, migrations, qcluster verification
**Avoids:** SQLite locking, retry misconfiguration

**Scope:**
- Install django-q2
- Configure Q_CLUSTER with SQLite-safe settings
- Enable WAL mode
- Run migrations
- Verify qcluster starts
- Test with simple echo task

### Phase 2: CedulaInfo Model
**Rationale:** Model must exist before tasks can write to it
**Delivers:** Data storage for scraped cedula information
**Implements:** CedulaInfo model with all status choices
**Dependencies:** Phase 1 (Django-Q2 migrations complete)

**Scope:**
- Create CedulaInfo model with status enum
- Add voting location fields (nullable)
- Add metadata fields (fetched_at, error_message)
- Run migration
- Register in admin

### Phase 3: Playwright Scraper
**Rationale:** Scraping logic should be tested standalone before task integration
**Delivers:** Working scraper that handles all Registraduria response types
**Implements:** scrapers.py module
**Avoids:** F5 detection (via stealth), memory leaks (via fresh instances)

**Scope:**
- Install playwright, playwright-stealth
- Run playwright install chromium
- Create scrape_registraduria function
- Handle found/not_found/cancelled/error states
- Test standalone (not as background task)
- Apply stealth patches

### Phase 4: Task Integration
**Rationale:** Combines model and scraper into background workflow
**Delivers:** End-to-end task execution with result persistence
**Implements:** tasks.py with fetch_cedula_info
**Uses:** CedulaInfo model, Playwright scraper

**Scope:**
- Create fetch_cedula_info task
- Wire to CedulaInfo model updates
- Test via Django shell async_task()
- Verify results in admin

### Phase 5: Signal Wiring
**Rationale:** Auto-trigger depends on working task
**Delivers:** Automatic cedula fetch on user registration
**Implements:** signals.py with post_save handler
**Avoids:** Race condition (via on_commit)

**Scope:**
- Create signals.py
- Use transaction.on_commit for task dispatch
- Update apps.py ready()
- Test: create user, verify task queued
- Verify CedulaInfo populated

### Phase 6: Manual Refresh
**Rationale:** Secondary trigger, simple once task works
**Delivers:** User-triggered re-validation capability
**Implements:** refresh_cedula_info view + URL

**Scope:**
- Add view with rate limiting (1/hour)
- Add URL pattern
- Test logged-in refresh flow

### Phase Ordering Rationale

1. **Foundation first:** Django-Q2 and SQLite config must be solid before any tasks
2. **Model before tasks:** Tasks need somewhere to store results
3. **Scraper isolated:** Testing Playwright independently simplifies debugging
4. **Task integration:** Combines model + scraper
5. **Signal last:** Depends on everything working
6. **Refresh is optional:** Can be skipped if time-constrained

### Research Flags

**Needs deeper research during planning:**
- **Phase 3 (Playwright Scraper):** F5 bypass effectiveness uncertain. May need to iterate on stealth config. Consider fallback to patchright if playwright-stealth insufficient.

**Standard patterns (skip research-phase):**
- **Phase 1 (Django-Q2):** Well-documented, official docs sufficient
- **Phase 2 (CedulaInfo Model):** Standard Django model patterns
- **Phase 4-6:** Standard Django patterns for tasks, signals, views

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Verified via official docs, PyPI, GitHub |
| Features | MEDIUM | F5 bypass success rate uncertain |
| Architecture | HIGH | Django-Q2 + Playwright pattern well-documented |
| Pitfalls | HIGH | Multiple sources, GitHub issues confirm |

**Overall confidence:** HIGH (with acknowledged uncertainty in bot detection)

### Gaps to Address

1. **F5 bypass effectiveness:** Cannot guarantee playwright-stealth will work. Test early in Phase 3. Have patchright as backup.

2. **Registraduria page structure:** Actual CSS selectors for data extraction TBD. Scraper needs manual inspection of live page.

3. **Python 3.14 compatibility:** Django-Q2 officially supports up to 3.13. May work but untested.

4. **Production deployment:** Chromium binary installation for production server not covered. May need Dockerfile or install script.

## Sources

### Primary (HIGH confidence)
- [Django-Q2 Official Docs](https://django-q2.readthedocs.io/) - Configuration, brokers, tasks
- [Playwright Python Docs](https://playwright.dev/python/docs/intro) - Installation, sync API
- [Django Signals Docs](https://docs.djangoproject.com/en/5.1/topics/signals/) - post_save patterns
- [PyPI Package Pages](https://pypi.org/) - Version verification

### Secondary (MEDIUM confidence)
- [playwright-stealth GitHub](https://github.com/AtuboDad/playwright_stealth) - Stealth configuration
- [Django-Q GitHub Issues](https://github.com/Koed00/django-q/issues/617) - SQLite locking solutions
- [Playwright GitHub Issues](https://github.com/microsoft/playwright-python/issues/1207) - Multiprocessing patterns

### Tertiary (LOW confidence)
- [ZenRows F5 Bypass Guide](https://www.zenrows.com/blog/bypass-f5) - F5 detection patterns
- [BrightData Stealth Blog](https://brightdata.com/blog/how-tos/avoid-bot-detection-with-playwright-stealth) - Bot evasion techniques

---
*Research completed: 2026-01-19*
*Ready for roadmap: yes*
