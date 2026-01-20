# Phase 13: Playwright Scraper - Research

**Researched:** 2026-01-20
**Domain:** Web scraping with Playwright for Python, bot evasion, headless browser automation
**Confidence:** HIGH

## Summary

Phase 13 implements a Playwright-based scraper to retrieve census data from Colombia's Registraduria electoral database. The scraper will look up cedula numbers and extract voting location information (departamento, municipio, puesto, direccion, mesa) or detect cancelled/not-found statuses.

The Registraduria site uses F5 Client Security Personal Module (CSPM) for bot detection, which sets security cookies and monitors page load timing. Per CONTEXT.md decisions, we use minimal stealth (no playwright-stealth initially) and build for graceful failure when blocked.

**Primary recommendation:** Use Playwright's sync API with browser instance reuse, Locator-based element selection with `wait_for()` for dynamic content, and return structured dicts with status codes instead of raising exceptions.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| playwright | 1.50+ | Browser automation | Microsoft-maintained, auto-waiting, modern API, Python async/sync support |
| playwright-stealth | 2.0.1 | Stealth patches (optional) | Port of puppeteer-extra-plugin-stealth, prepared for future use |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-decouple | 3.8+ | Environment config | Already installed, use for DEBUG check |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| playwright | selenium | Playwright has better auto-waiting, faster, less flaky |
| playwright | requests + BeautifulSoup | Would work for static pages, but Registraduria uses JS rendering |
| playwright-stealth | undetected-playwright | More aggressive patching, but less maintained |

**Installation:**
```bash
pip install playwright
playwright install chromium
```

Note: `playwright install chromium` downloads Chromium binary (~150MB). For headless-only scenarios, use `playwright install chromium --only-shell` to save space.

## Architecture Patterns

### Recommended Project Structure
```
___/accounts/
    scraper.py         # Scraper module (new)
    tasks.py           # Django-Q2 tasks (update in Phase 14)
    models.py          # CedulaInfo model (exists)
```

### Pattern 1: Singleton Browser with Context Clearing
**What:** Reuse browser instance across scrapes, create fresh context per scrape
**When to use:** Multiple sequential scrapes within one worker process
**Example:**
```python
# Source: Playwright docs - BrowserContext
class RegistraduriaScraper:
    _browser = None

    @classmethod
    def get_browser(cls):
        if cls._browser is None:
            from playwright.sync_api import sync_playwright
            cls._playwright = sync_playwright().start()
            cls._browser = cls._playwright.chromium.launch(
                headless=not settings.DEBUG
            )
        return cls._browser

    def scrape(self, cedula: str) -> dict:
        browser = self.get_browser()
        context = browser.new_context()
        try:
            page = context.new_page()
            # ... scraping logic
        finally:
            context.close()  # Clean state for next scrape
```

### Pattern 2: Status-Based Return Values (No Exceptions)
**What:** Return dict with status field instead of raising exceptions
**When to use:** When caller needs to distinguish error types for retry logic
**Example:**
```python
# Source: CONTEXT.md decisions
def scrape_cedula(cedula: str) -> dict:
    """
    Returns:
        {'status': 'found', 'departamento': '...', 'municipio': '...', ...}
        {'status': 'not_found'}
        {'status': 'cancelled', 'novedad': '...', 'fecha_novedad': '...'}
        {'status': 'blocked', 'raw_html': '...'}
        {'status': 'timeout', 'error': '...'}
        {'status': 'network_error', 'error': '...'}
        {'status': 'parse_error', 'raw_html': '...', 'error': '...'}
    """
```

### Pattern 3: Locator-Based Element Selection with Explicit Waits
**What:** Use Locators instead of ElementHandles, with explicit wait_for() for dynamic content
**When to use:** When page content loads dynamically after form submission
**Example:**
```python
# Source: Playwright docs - Locator API
# Fill form and submit
page.locator('input[type="text"]').fill(cedula)
page.locator('button:has-text("Consultar")').click()

# Wait for result element to appear (dynamic content)
result_locator = page.locator('#resultado, .error-message')
result_locator.wait_for(state='visible', timeout=90000)

# Extract text
text = result_locator.text_content()
```

### Anti-Patterns to Avoid
- **time.sleep() for waits:** Use `wait_for()` or Playwright's auto-waiting instead; fixed delays are slow and flaky
- **ElementHandle for repeated queries:** Use Locators; they re-query the DOM and handle stale references
- **Raising exceptions for expected failures:** Return status dict; task layer handles retry logic
- **Storing raw HTML on success:** Only store on error for debugging (per CONTEXT.md)

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Bot detection evasion | Custom UA rotation | playwright-stealth (if needed) | Handles webdriver flag, UA, plugins, etc. |
| Element waiting | Manual retry loops | `locator.wait_for()` | Built-in timeout, state options, auto-retry |
| Form filling | Manual input simulation | `locator.fill()` | Handles focus, clear, input events automatically |
| Page load detection | Checking document.ready | `page.goto(wait_until='networkidle')` | Built-in network monitoring |
| Screenshot on error | Manual capture logic | (not needed per CONTEXT.md) | Explicitly deferred |

**Key insight:** Playwright's Locator API handles most timing issues automatically. The main challenge is identifying the correct selectors for the Registraduria page and handling its various response states.

## Common Pitfalls

### Pitfall 1: Headless Detection by F5 CSPM
**What goes wrong:** Registraduria's F5 CSPM detects headless browsers via fingerprinting
**Why it happens:** F5 monitors page load timing, checks navigator.webdriver, and analyzes browser properties
**How to avoid:**
1. Start with minimal approach (headless=False in DEBUG mode for testing)
2. If blocked, add playwright-stealth
3. Build graceful 'blocked' status handling from day one
**Warning signs:** Immediate block page, CAPTCHA, or "access denied" after form submission

### Pitfall 2: Timeout on Slow Registraduria Response
**What goes wrong:** Scraper times out before page finishes loading
**Why it happens:** Registraduria server can be slow, especially during peak times
**How to avoid:**
1. Set 90-second timeout (per CONTEXT.md)
2. Use `wait_until='domcontentloaded'` for initial load (faster than networkidle)
3. Use explicit `wait_for()` for result element
**Warning signs:** Consistent timeouts during certain hours

### Pitfall 3: Selector Fragility
**What goes wrong:** Scraper breaks when Registraduria updates their HTML
**Why it happens:** CSS selectors tied to specific class names or structure
**How to avoid:**
1. Use semantic selectors where possible (button:has-text("Consultar"))
2. Log raw HTML on parse_error for debugging
3. Keep selectors in constants at module top for easy updates
**Warning signs:** parse_error status with valid HTML in raw_response

### Pitfall 4: Browser Instance Memory Leak
**What goes wrong:** Memory grows over time as browser accumulates state
**Why it happens:** Not closing contexts, keeping old pages open
**How to avoid:**
1. Always close context in finally block
2. Create fresh context per scrape (reuse browser)
3. Consider browser.close() and restart after N scrapes if issues persist
**Warning signs:** Worker process memory growing over time

### Pitfall 5: Race Condition on Browser Initialization
**What goes wrong:** Multiple tasks try to initialize browser simultaneously
**Why it happens:** Django-Q2 worker starts tasks before browser is ready
**How to avoid:**
1. Use class-level singleton pattern with lazy initialization
2. Single worker (workers=1) already configured
3. Initialize browser at module import if needed
**Warning signs:** "Browser not initialized" errors in logs

## Code Examples

Verified patterns from official sources:

### Browser Launch with Headless Toggle
```python
# Source: https://playwright.dev/python/docs/library
from django.conf import settings
from playwright.sync_api import sync_playwright

def launch_browser():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=not settings.DEBUG,  # Headed in DEBUG mode
        # channel='chromium' for new headless mode (more Chrome-like)
    )
    return playwright, browser
```

### Form Fill and Submit with Wait
```python
# Source: https://playwright.dev/python/docs/api/class-locator
def fill_and_submit(page, cedula: str):
    # Fill cedula input
    cedula_input = page.locator('input#cedula, input[name="cedula"]')
    cedula_input.fill(cedula)

    # Click submit button
    submit_btn = page.locator('button:has-text("Consultar")')
    submit_btn.click()

    # Wait for result to appear (either success or error)
    page.locator('#resultado, .mensaje-error').wait_for(
        state='visible',
        timeout=90000  # 90 seconds per CONTEXT.md
    )
```

### Extract Text with Null Handling
```python
# Source: https://playwright.dev/python/docs/api/class-locator
def extract_field(page, selector: str) -> str | None:
    """Extract text from selector, return None if not found."""
    locator = page.locator(selector)
    if locator.count() > 0:
        text = locator.first.text_content()
        return text.strip() if text else None
    return None
```

### Exception Handling Pattern
```python
# Source: https://playwright.dev/python/docs/api/class-timeouterror
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import logging

logger = logging.getLogger('django-q')

def scrape_with_error_handling(page, cedula: str) -> dict:
    try:
        page.goto(URL, timeout=30000, wait_until='domcontentloaded')
        # ... scraping logic
        return {'status': 'found', ...}
    except PlaywrightTimeoutError as e:
        logger.error(f"Timeout scraping cedula {cedula}: {e}")
        return {'status': 'timeout', 'error': str(e)}
    except Exception as e:
        logger.error(f"Network error scraping cedula {cedula}: {e}")
        return {'status': 'network_error', 'error': str(e)}
```

### Context Cleanup Pattern
```python
# Source: https://playwright.dev/python/docs/api/class-browsercontext
def scrape_cedula(cedula: str) -> dict:
    browser = get_browser()
    context = browser.new_context()
    try:
        page = context.new_page()
        page.set_default_timeout(90000)  # 90s default
        result = _do_scrape(page, cedula)
        return result
    finally:
        context.close()  # Always cleanup
```

### Django Logging Integration
```python
# Source: Django docs + CONTEXT.md decisions
import logging

# Use django-q logger (already configured in settings.py)
logger = logging.getLogger('django-q')

def scrape_cedula(cedula: str) -> dict:
    result = _do_scrape(cedula)

    # INFO: just status (production)
    logger.info(f"Scrape {cedula}: {result['status']}")

    # DEBUG: extracted text (development)
    if result['status'] == 'found':
        logger.debug(f"Extracted: {result}")

    return result
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| page.waitForSelector() | locator.wait_for() | Playwright 1.14+ | Locator API is recommended, auto-retry on stale |
| ElementHandle | Locator | Playwright 1.14+ | Locators are more robust, re-query DOM |
| headless: true | channel: 'chromium' | Playwright 1.21+ | New headless mode more Chrome-like |
| puppeteer-stealth | playwright-stealth 2.0.1 | Jan 2026 | Python-native, updated fork |

**Deprecated/outdated:**
- `page.$(selector)` / `page.$$(selector)`: Use `page.locator(selector)` instead
- `page.waitForSelector()`: Use `locator.wait_for()` for better ergonomics
- Fixed time.sleep() delays: Use Playwright's auto-waiting or explicit wait_for()

## Target Site Analysis

### Registraduria Electoral Census Lookup
**URL:** https://consultacenso.registraduria.gov.co/consultar/

**Form Elements (observed):**
- Cedula input field (text input for ID number)
- Election dropdown (select with election options)
- Verification checkbox
- "Consultar" submit button

**Security Measures:**
- F5 CSPM (Client Security Personal Module) JavaScript
- Monitors page load timing
- Sets security cookies
- Bot detection infrastructure

**Expected Responses:**
1. **Active cedula:** Shows "INFORMACION DEL LUGAR DE VOTACION" with departamento, municipio, puesto, direccion, mesa
2. **Cancelled cedula:** Shows novedad (reason), resolucion, fecha_novedad
3. **Not found:** Error message indicating cedula not in census
4. **Blocked:** F5 challenge page or access denied

**Note:** Exact CSS selectors need to be determined during implementation by inspecting the live page. The CONTEXT.md grants discretion for selector decisions.

## Open Questions

Things that couldn't be fully resolved:

1. **Exact CSS selectors for Registraduria page**
   - What we know: Form has cedula input, dropdown, checkbox, submit button
   - What's unclear: Exact element IDs, classes, or structure for result fields
   - Recommendation: Inspect live page during implementation, document selectors as constants

2. **F5 CSPM detection threshold**
   - What we know: F5 monitors timing and browser properties
   - What's unclear: Whether minimal headless (no stealth) will pass or trigger block
   - Recommendation: Start minimal, add playwright-stealth if blocked consistently

3. **Election dropdown requirement**
   - What we know: Dropdown exists with "Seleccione la eleccion" options
   - What's unclear: Whether it needs selection or has a default
   - Recommendation: Test with real cedula during implementation

## Sources

### Primary (HIGH confidence)
- [Playwright Python Installation](https://playwright.dev/python/docs/intro) - Installation commands, system requirements
- [Playwright Python Library](https://playwright.dev/python/docs/library) - Sync/async API, browser launch options
- [BrowserContext API](https://playwright.dev/python/docs/api/class-browsercontext) - clear_cookies(), new_page(), context management
- [Page API](https://playwright.dev/python/docs/api/class-page) - goto(), locator(), set_default_timeout()
- [Locator API](https://playwright.dev/python/docs/api/class-locator) - wait_for(), fill(), click(), text_content()
- [TimeoutError](https://playwright.dev/python/docs/api/class-timeouterror) - Exception handling pattern

### Secondary (MEDIUM confidence)
- [playwright-stealth PyPI](https://pypi.org/project/playwright-stealth/) - Version 2.0.1, usage example, limitations
- [BrowserStack Wait Types Guide](https://www.browserstack.com/guide/playwright-wait-types) - wait_for states, best practices
- [Registraduria Census Lookup](https://consultacenso.registraduria.gov.co/consultar/) - Target site structure (WebFetch analysis)

### Tertiary (LOW confidence)
- WebSearch results on F5 CSPM bypass - No specific F5 CSPM documentation found; general bot evasion patterns apply

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Playwright Python docs are authoritative and current
- Architecture: HIGH - Patterns derived from official documentation
- Pitfalls: MEDIUM - F5 CSPM behavior is speculative, based on general bot detection knowledge
- Target site selectors: LOW - Need live inspection during implementation

**Research date:** 2026-01-20
**Valid until:** 2026-02-20 (30 days for stable library, site structure may change)
