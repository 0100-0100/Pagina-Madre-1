# Features Research: v1.3 Async Background Jobs

**Domain:** Background task processing + web scraping for Colombian Registraduria census lookup
**Researched:** 2026-01-19
**Confidence:** MEDIUM (verified against multiple sources, but F5 anti-bot bypass is inherently uncertain)

## Executive Summary

Building a background task system for cedula validation against the Registraduria's JavaScript-rendered, F5-protected census page requires two core capabilities: (1) a task queue that works with SQLite, and (2) a headless browser that can handle anti-bot protection. Django-Q2 is the right choice for task queue (lightweight, SQLite-compatible), and Playwright with stealth patches is the best option for scraping.

The F5 CSPM anti-bot protection presents the highest risk factor. This is not a guaranteed-success domain - expect some failures and build the system to handle them gracefully.

---

## Table Stakes (Must Have)

Features users expect. Missing = system doesn't work.

| Feature | Why Required | Complexity | Depends On |
|---------|--------------|------------|------------|
| **Task queue system** | Execute scraping outside request cycle; prevents timeouts | Medium | Django-Q2 package |
| **Headless browser scraping** | Target site is JavaScript-rendered; HTTP requests won't work | High | Playwright + browsers |
| **Retry logic with exponential backoff** | F5 protection and network issues cause transient failures | Medium | Task queue |
| **CedulaInfo model** | Store scraped data persistently for display | Low | Django ORM |
| **Status tracking** | Users need to know if lookup is pending/complete/failed | Low | CedulaInfo model |
| **Auto-trigger on registration** | Core use case - validate new users automatically | Low | Task queue + signals |
| **Error handling for all response types** | Three response types (active, cancelled, not found) plus errors | Medium | Scraper logic |
| **Rate limiting** | Prevent triggering aggressive bot detection | Medium | Task queue config |
| **Task timeout handling** | Scraping can hang; must not block queue | Low | Task queue config |

### Task Queue System Details

**Recommended:** Django-Q2 (fork of Django-Q, actively maintained)

Why Django-Q2 over Celery:
- Works with SQLite database as broker (no Redis/RabbitMQ required)
- Simpler configuration (~10 lines vs 50+ for Celery)
- Django-native admin integration
- Sufficient for <100 users scale
- 40% of Django projects use Django-Q style solutions for simple workloads

Celery is overkill for this use case - it requires external message brokers (Redis/RabbitMQ) and has significantly more configuration complexity.

### Headless Browser Scraping Details

**Recommended:** Playwright with stealth patches

Why Playwright over Selenium:
- Faster execution (uses Chrome DevTools Protocol)
- Native async support (matches Django-Q2's async capabilities)
- Better auto-waiting for dynamic content
- Modern API with better error messages
- Microsoft-backed with active development

Why stealth patches are essential:
- F5 CSPM detects standard Playwright via `navigator.webdriver` property
- Stealth patches remove automation indicators
- Options: `playwright-stealth` or `undetected-playwright-python`

### CedulaInfo Model Requirements

| Field | Type | Purpose | Notes |
|-------|------|---------|-------|
| `user` | OneToOneField | Link to CustomUser | Primary key reference |
| `status` | CharField | Current validation state | Choices: pending, active, cancelled, not_found, error |
| `departamento` | CharField | Voting department | Nullable for non-active |
| `municipio` | CharField | Voting municipality | Nullable for non-active |
| `puesto` | CharField | Voting location name | Nullable for non-active |
| `direccion` | TextField | Voting location address | Nullable for non-active |
| `mesa` | CharField | Voting table number | Nullable for non-active |
| `novedad` | CharField | Cancellation type | Only for cancelled status |
| `resolucion` | CharField | Cancellation resolution | Only for cancelled status |
| `fecha_novedad` | DateField | Cancellation date | Only for cancelled status |
| `last_checked` | DateTimeField | When last scraped | Track data freshness |
| `last_error` | TextField | Last error message | Nullable, for debugging |
| `check_count` | IntegerField | Number of lookup attempts | Track retry history |
| `created_at` | DateTimeField | Record creation | auto_now_add |
| `updated_at` | DateTimeField | Last modification | auto_now |

---

## Nice-to-Haves

Features that improve reliability or UX but aren't strictly required.

| Feature | Value | Complexity | Priority |
|---------|-------|------------|----------|
| **Manual refresh button** | User can request re-validation if data stale | Low | High |
| **Task progress visibility** | Show "checking..." status in UI | Low | High |
| **Scheduled re-validation** | Keep data fresh periodically | Medium | Medium |
| **Proxy rotation** | Distribute requests across IPs to avoid blocks | High | Low |
| **Browser fingerprint randomization** | Reduce detection probability | Medium | Low |
| **Task result caching** | Avoid re-scraping same cedula within time window | Low | Medium |
| **Batch processing** | Process multiple cedulas in single browser session | Medium | Low |
| **Admin dashboard for task monitoring** | View pending/failed tasks in Django admin | Low | Medium |
| **Failure notifications** | Alert admin when error rate spikes | Medium | Low |
| **Graceful degradation UI** | Show partial info if some fields fail | Low | Medium |

### Manual Refresh Details

- Add "Actualizar datos" button on profile/home page
- Check rate limit (e.g., max 1 refresh per hour per user)
- Show last_checked timestamp for transparency
- Disable button while task is pending

### Task Progress Visibility Details

- Show spinner/badge when status is "pending"
- WebSocket not needed - simple page refresh or polling sufficient for <100 users
- Consider JavaScript polling every 10 seconds while pending

---

## Anti-Features (Avoid)

Things to deliberately NOT build. Common mistakes in this domain.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Real-time scraping in request** | Timeout errors, poor UX, blocks web server | Background task queue |
| **Unlimited retry attempts** | Can loop forever on permanent failures | Max 3-5 retries with backoff |
| **Storing Registraduria session cookies** | Security risk, cookies expire quickly anyway | Fresh browser session each time |
| **Aggressive request rate** | Triggers bot detection, IP bans | 1 request per 5+ seconds minimum |
| **Single browser instance shared** | Race conditions, memory leaks | Fresh browser per task or pool |
| **Scraping in main thread** | Blocks all other requests | Dedicated worker process |
| **Complex anti-bot bypass logic** | Arms race with F5, maintenance burden | Accept some failures, handle gracefully |
| **User-visible error details** | Exposes system internals | Generic "could not verify" message |
| **Sync Playwright in async context** | Blocks event loop, defeats purpose | Use async Playwright API |
| **Storing raw HTML responses** | Storage bloat, PII concerns | Extract only needed fields |
| **Hardcoded selectors without fallbacks** | Site changes break scraper silently | Selector validation + fallbacks |
| **Silent failure on scrape errors** | Users left confused | Always update status, even on failure |

### Why NOT to Build Proxy Rotation (Initially)

- Adds significant complexity (proxy provider integration)
- Cost for residential proxies ($50-500/month for quality)
- Overkill for <100 users with modest request volume
- F5 primarily detects automation patterns, not just IPs
- Better ROI: improve stealth browser config first

### Why NOT to Build Scheduled Re-validation (Initially)

- Electoral census data rarely changes (once per election cycle typically)
- Adds scheduler complexity (Celery Beat or Django-Q scheduled tasks)
- User-triggered refresh sufficient for MVP
- Can add later when there's clear need

---

## Response Type Handling

The Registraduria census lookup returns three distinct response types:

### 1. Active Voter (ACTIVO)

**Indicators:** Page shows voting location details
**Data to extract:**
- Departamento
- Municipio
- Puesto de votacion (name)
- Direccion (address)
- Mesa (table number)

**Status:** `active`

### 2. Cancelled Registration (CANCELADO)

**Indicators:** Page shows cancellation notice
**Data to extract:**
- Tipo de novedad (e.g., "FALLECIDO")
- Numero de resolucion
- Fecha de la novedad

**Status:** `cancelled`

### 3. Not Found

**Indicators:** Page shows "no se encontro" or similar message
**Data to extract:** None

**Status:** `not_found`

### 4. Error States

**Indicators:** Timeout, connection error, unexpected page structure, bot detection page
**Data to extract:** Error message for logs

**Status:** `error`

---

## Task Queue Configuration

### Django-Q2 Recommended Settings

```python
Q_CLUSTER = {
    'name': 'cedula-validation',
    'workers': 1,  # Single worker sufficient for <100 users
    'timeout': 120,  # 2 minutes per task max
    'retry': 180,  # Retry failed tasks after 3 minutes
    'queue_limit': 50,  # Max pending tasks
    'bulk': 1,  # Process one at a time (rate limiting)
    'orm': 'default',  # Use SQLite via Django ORM
    'catch_up': False,  # Don't run missed scheduled tasks
}
```

### Rate Limiting Strategy

- **Minimum delay between requests:** 5 seconds
- **Exponential backoff on failure:** 30s, 60s, 120s
- **Max retries per cedula:** 3
- **Daily limit per user:** 5 refresh requests
- **Concurrent browser instances:** 1 (serialize all scraping)

---

## Complexity Assessment

| Component | Lines of Code (Est.) | Risk Level | Notes |
|-----------|---------------------|------------|-------|
| CedulaInfo model | ~50 | Low | Standard Django model |
| Django-Q2 setup | ~30 | Low | Well-documented, Django-native |
| Playwright scraper | ~150 | High | F5 detection is unpredictable |
| Stealth configuration | ~50 | Medium | May need tuning |
| Task registration | ~30 | Low | Signal + async_task call |
| Status display UI | ~50 | Low | Template additions |
| Manual refresh | ~40 | Low | View + rate limit logic |
| Error handling | ~80 | Medium | Multiple failure modes |
| **Total** | ~480 | Medium-High | F5 bypass is main risk |

---

## Dependencies on Existing Features

| New Feature | Depends On | Integration Point |
|-------------|------------|-------------------|
| CedulaInfo model | CustomUser model | OneToOneField relationship |
| Auto-trigger on registration | User registration view | Django signal (post_save) |
| Manual refresh | Authentication system | @login_required decorator |
| Status display | Home page template | Add CedulaInfo context |
| Profile integration | Profile page | Show validation status |

---

## MVP Recommendation

For MVP, implement in this order:

1. **CedulaInfo model** - Data storage foundation
2. **Django-Q2 setup** - Task queue infrastructure
3. **Basic Playwright scraper** - Core scraping logic (without stealth initially)
4. **Registration trigger** - Auto-validate new users
5. **Status display** - Show results on home/profile page
6. **Stealth patches** - Add if basic scraper gets blocked
7. **Retry logic** - Handle transient failures
8. **Manual refresh** - User-triggered re-validation

**Defer to post-MVP:**
- Proxy rotation (only if consistently blocked)
- Scheduled re-validation (only if data freshness becomes issue)
- Batch processing (only if queue backs up)
- Advanced monitoring (only if debugging becomes painful)

---

## Risk Factors

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| F5 blocks all scraping attempts | Medium | High | Stealth config, accept some failures |
| Registraduria changes page structure | Low | High | Flexible selectors, error alerts |
| Playwright crashes/memory leaks | Medium | Medium | Task timeout, browser restart |
| SQLite locks under load | Low | Medium | Single worker, serialize tasks |
| Rate limiting triggers captcha | Medium | Medium | Slower request rate, backoff |

---

## Sources

### Task Queue / Background Jobs
- [Real Python - Asynchronous Tasks With Django and Celery](https://realpython.com/asynchronous-tasks-with-django-and-celery/)
- [Medium - Django Background Tasks Guide: Celery vs Django-Q](https://medium.com/@anas-issath/the-django-background-tasks-guide-celery-vs-django-q-vs-alternatives-6b249e13316a)
- [Medium - Lightweight Django Task Queues in 2025](https://medium.com/@g.suryawanshi/lightweight-django-task-queues-in-2025-beyond-celery-74a95e0548ec)
- [Medium - Celery Beat: Background Tasks in Django](https://medium.com/@alfininfo/celery-beat-the-best-solution-for-background-tasks-in-django-memory-optimization-tips-e582c1d080af)

### Retry and Error Handling
- [Medium - Retrying Failed Tasks in Django with Celery](https://medium.com/@dharmateja.k/retrying-failed-tasks-in-django-with-celery-f2f349fab9ca)
- [Vinta Software - Advanced Celery: Idempotency, Retries & Error Handling](https://www.vintasoftware.com/blog/celery-wild-tips-and-tricks-run-async-tasks-real-world)
- [GitGuardian - Celery Task Resilience: Advanced Strategies](https://blog.gitguardian.com/celery-tasks-retries-errors/)

### Web Scraping / Playwright
- [Scrapfly - Web Scraping with Playwright and Python](https://scrapfly.io/blog/posts/web-scraping-with-playwright-and-python)
- [ZenRows - Scraping JavaScript-Rendered Web Pages (2026)](https://www.zenrows.com/blog/scraping-javascript-rendered-web-pages)
- [BrowserStack - Web Scraping with Playwright (2026)](https://www.browserstack.com/guide/playwright-web-scraping)
- [ZenRows - Playwright Stealth Usage](https://www.zenrows.com/blog/playwright-stealth)

### Anti-Bot Bypass
- [ZenRows - How to Bypass F5 Antibot (2026)](https://www.zenrows.com/blog/bypass-f5)
- [BrightData - Avoiding Bot Detection with Playwright Stealth](https://brightdata.com/blog/how-tos/avoid-bot-detection-with-playwright-stealth)
- [ScrapingAnt - Make Playwright Scraping Undetectable](https://scrapingant.com/blog/playwright-scraping-undetectable)
- [GitHub - undetected-playwright-python](https://github.com/kaliiiiiiiiii/undetected-playwright-python)

### Rate Limiting
- [Scrape.do - Rate Limit in Web Scraping](https://scrape.do/blog/web-scraping-rate-limit/)
- [Oxylabs - What Is Rate Limiting & How to Avoid It](https://oxylabs.io/blog/rate-limiting)
- [Apify - Rate Limiting Techniques](https://docs.apify.com/academy/anti-scraping/techniques/rate-limiting)

### Django Integration
- [Scrapy Django Dashboard Docs](https://scrapy-django-dashboard.readthedocs.io/en/latest/getting_started.html)
- [Celery Result Backends Best Practices](https://pythonroadmap.com/blog/celery-result-backends-options-and-best-practices)

---

*Feature research completed: 2026-01-19*
