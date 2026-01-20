"""
Registraduria Census Data Scraper

This module provides a headless browser scraper for retrieving electoral
census data from Colombia's Registraduria. It uses Playwright to navigate
the census lookup page and 2captcha to solve the reCAPTCHA challenge.

The scraper implements a browser singleton pattern for performance:
- Browser instance is reused across scrapes (lazy initialization)
- Fresh browser context is created per scrape for isolation
- Context cleanup happens in finally block to ensure clean state

Usage:
    scraper = RegistraduriaScraper()
    result = scraper.scrape_cedula('12345678')
    # Returns dict with status and data fields

Status codes:
    - 'found': Cedula found with voting location data
    - 'cancelled': Cedula cancelled (deceased or other)
    - 'not_found': Cedula not in census
    - 'captcha_failed': 2captcha failed to solve reCAPTCHA
    - 'timeout': Page or element timeout
    - 'network_error': Connection failed
    - 'parse_error': Unable to extract results
"""

import logging
import time

from django.conf import settings
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from twocaptcha import TwoCaptcha
from twocaptcha.api import ApiException


# Constants
REGISTRADURIA_URL = 'https://consultacenso.registraduria.gov.co/consultar/'
DEFAULT_TIMEOUT = 90000  # 90 seconds in milliseconds
RATE_LIMIT_SECONDS = 5  # Minimum seconds between requests
PAGE_LOAD_TIMEOUT = 60000  # 60 seconds for initial page load
CAPTCHA_TIMEOUT = 120  # 2 minutes for 2captcha to solve

# CSS Selectors based on actual Registraduria page structure
SELECTORS = {
    # Page loading indicator
    'spinner_overlay': '.loading, .spinner, .overlay, [class*="loading"]',
    # Form elements
    'cedula_input': 'input[type="text"], input[type="number"], input#cedula, input[name="cedula"]',
    'election_dropdown': 'select',
    'submit_button': 'button:has-text("CONSULTAR"), input[type="submit"]:has-text("CONSULTAR"), button:has-text("Consultar")',
    # reCAPTCHA
    'recaptcha_iframe': 'iframe[src*="recaptcha"]',
    'recaptcha_response': '#g-recaptcha-response, textarea[name="g-recaptcha-response"]',
    # Results table
    'results_table': 'table',
    'results_row': 'table tbody tr, table tr:not(:first-child)',
}

# Text patterns for detecting response types
PATTERNS = {
    'cancelled': ['CANCELADA POR', 'FALLECIDO', 'MUERTE'],
    'not_found': ['NO SE ENCUENTRA EN EL CENSO', 'NO SE ENCUENTRA', 'NO ENCONTRADO', 'NO APARECE', 'NO EXISTE', 'SIN RESULTADOS'],
}

# Logger integrates with existing django-q logging config
logger = logging.getLogger('django-q')


class RegistraduriaScraper:
    """
    Scraper for Registraduria electoral census data.

    Uses browser singleton pattern:
    - _playwright and _browser are class-level singletons
    - get_browser() performs lazy initialization
    - close_browser() cleans up resources
    - Each scrape_cedula() call creates a fresh context

    Rate limiting:
    - _last_request_time tracks last scrape across all instances
    - _enforce_rate_limit() ensures minimum 5 seconds between requests
    """

    _playwright = None
    _browser = None
    _last_request_time: float = 0  # Class-level rate limiting tracker

    @classmethod
    def _enforce_rate_limit(cls):
        """
        Ensure minimum 5 seconds between requests.

        Sleeps if needed to maintain rate limit, preventing
        excessive requests to Registraduria servers.
        """
        elapsed = time.time() - cls._last_request_time
        if elapsed < RATE_LIMIT_SECONDS:
            sleep_time = RATE_LIMIT_SECONDS - elapsed
            logger.debug("Rate limiting: sleeping %.1fs", sleep_time)
            time.sleep(sleep_time)
        cls._last_request_time = time.time()

    @classmethod
    def get_browser(cls):
        """
        Get or create the browser singleton.

        Browser is launched in headless mode by default.
        In DEBUG mode, browser runs headed for visual debugging.

        Returns:
            Browser: Playwright Chromium browser instance
        """
        if cls._browser is None:
            logger.debug("Initializing Playwright browser singleton")
            cls._playwright = sync_playwright().start()
            cls._browser = cls._playwright.chromium.launch(
                headless=not settings.DEBUG
            )
            logger.info("Playwright browser initialized (headless=%s)",
                       not settings.DEBUG)
        return cls._browser

    @classmethod
    def close_browser(cls):
        """
        Close the browser singleton and cleanup resources.

        Should be called when shutting down the worker or
        when browser needs to be restarted.
        """
        if cls._browser is not None:
            logger.debug("Closing Playwright browser")
            cls._browser.close()
            cls._browser = None
        if cls._playwright is not None:
            cls._playwright.stop()
            cls._playwright = None
            logger.info("Playwright browser closed")

    def _get_recaptcha_sitekey(self, page) -> str | None:
        """
        Extract the reCAPTCHA site key from the page.

        Looks for the data-sitekey attribute on the reCAPTCHA div
        or extracts it from the iframe src.

        Args:
            page: Playwright page object

        Returns:
            Site key string or None if not found
        """
        try:
            # Try to find data-sitekey attribute on reCAPTCHA div
            recaptcha_div = page.locator('[data-sitekey]')
            if recaptcha_div.count() > 0:
                sitekey = recaptcha_div.first.get_attribute('data-sitekey')
                if sitekey:
                    logger.debug("Found reCAPTCHA sitekey: %s", sitekey[:20] + "...")
                    return sitekey

            # Fallback: extract from iframe src
            iframe = page.locator(SELECTORS['recaptcha_iframe'])
            if iframe.count() > 0:
                src = iframe.first.get_attribute('src')
                if src and 'k=' in src:
                    # Extract sitekey from URL parameter
                    import re
                    match = re.search(r'[?&]k=([^&]+)', src)
                    if match:
                        sitekey = match.group(1)
                        logger.debug("Extracted sitekey from iframe: %s", sitekey[:20] + "...")
                        return sitekey

        except Exception as e:
            logger.warning("Failed to extract reCAPTCHA sitekey: %s", str(e))

        return None

    def _solve_recaptcha(self, page, page_url: str) -> str | None:
        """
        Solve reCAPTCHA using 2captcha service.

        Args:
            page: Playwright page object
            page_url: URL of the page with reCAPTCHA

        Returns:
            Solved token string or None if failed
        """
        api_key = settings.TWOCAPTCHA_API_KEY
        if not api_key:
            logger.error("TWOCAPTCHA_API_KEY not configured")
            return None

        sitekey = self._get_recaptcha_sitekey(page)
        if not sitekey:
            logger.error("Could not find reCAPTCHA sitekey on page")
            return None

        try:
            logger.info("Sending reCAPTCHA to 2captcha for solving...")
            solver = TwoCaptcha(api_key)
            result = solver.recaptcha(
                sitekey=sitekey,
                url=page_url
            )
            token = result.get('code') if isinstance(result, dict) else result
            logger.info("reCAPTCHA solved successfully")
            return token

        except ApiException as e:
            logger.error("2captcha API error: %s", str(e))
            return None
        except Exception as e:
            logger.error("2captcha solving failed: %s", str(e))
            return None

    def _inject_captcha_token(self, page, token: str) -> bool:
        """
        Inject the solved reCAPTCHA token into the page.

        Sets the g-recaptcha-response textarea value and triggers
        the callback function if present.

        Args:
            page: Playwright page object
            token: Solved reCAPTCHA token

        Returns:
            True if injection succeeded, False otherwise
        """
        try:
            # Inject token into the hidden textarea
            page.evaluate(f'''() => {{
                // Find and fill the response textarea
                const textarea = document.getElementById('g-recaptcha-response') ||
                                document.querySelector('textarea[name="g-recaptcha-response"]');
                if (textarea) {{
                    textarea.value = "{token}";
                    textarea.style.display = 'block';  // Make visible temporarily for debugging
                }}

                // Try to trigger the callback if it exists
                if (typeof ___grecaptcha_cfg !== 'undefined') {{
                    const clients = ___grecaptcha_cfg.clients;
                    if (clients) {{
                        for (const key in clients) {{
                            const client = clients[key];
                            if (client && client.callback) {{
                                client.callback("{token}");
                            }}
                        }}
                    }}
                }}

                // Also try common callback patterns
                if (typeof grecaptchaCallback === 'function') {{
                    grecaptchaCallback("{token}");
                }}
                if (typeof onRecaptchaSuccess === 'function') {{
                    onRecaptchaSuccess("{token}");
                }}
            }}''')
            logger.debug("reCAPTCHA token injected into page")
            return True

        except Exception as e:
            logger.error("Failed to inject reCAPTCHA token: %s", str(e))
            return False

    def _wait_for_page_ready(self, page):
        """
        Wait for the page to be fully loaded and interactive.

        Waits for any loading spinners to disappear and for the
        form elements to be visible.

        Args:
            page: Playwright page object
        """
        # Wait for network to settle
        page.wait_for_load_state('networkidle', timeout=PAGE_LOAD_TIMEOUT)

        # Wait for any spinner/overlay to disappear
        try:
            spinner = page.locator(SELECTORS['spinner_overlay'])
            if spinner.count() > 0:
                spinner.first.wait_for(state='hidden', timeout=30000)
                logger.debug("Page spinner disappeared")
        except PlaywrightTimeoutError:
            logger.debug("No spinner found or already hidden")

        # Ensure form input is visible
        page.locator(SELECTORS['cedula_input']).first.wait_for(state='visible', timeout=30000)
        logger.debug("Page ready - form input visible")

    def _extract_results_from_table(self, page) -> dict:
        """
        Extract census data from the results area.

        Response types:
        - not_found: "no se encuentra en el censo" message
        - cancelled: Table with NUIP, NOVEDAD (Cancelada por...), RESOLUCIÓN, FECHA
        - found: Table with voting location data

        Args:
            page: Playwright page object with results displayed

        Returns:
            dict with status and extracted data
        """
        try:
            # Wait for results area to appear (either table or message)
            page.wait_for_timeout(2000)  # Give time for results to render

            # Get page content for pattern matching
            content = page.content().upper()

            # Check for "not found" FIRST - this appears as a message, not table data
            # Pattern: "no se encuentra en el censo para esta elección"
            if any(pattern in content for pattern in PATTERNS['not_found']):
                logger.info("Cedula not found in census")
                return {'status': 'not_found'}

            # Check for cancelled cedula (has table with "Cancelada por..." in NOVEDAD)
            if any(pattern in content for pattern in PATTERNS['cancelled']):
                # Extract cancelled cedula data from table
                rows = page.locator(SELECTORS['results_row'])
                if rows.count() > 0:
                    cells = rows.first.locator('td')
                    cell_texts = [cells.nth(i).text_content().strip()
                                 for i in range(cells.count())]

                    # Table structure: NUIP | NOVEDAD | RESOLUCIÓN | FECHA NOVEDAD
                    result = {
                        'status': 'cancelled',
                        'nuip': cell_texts[0] if len(cell_texts) > 0 else None,
                        'novedad': cell_texts[1] if len(cell_texts) > 1 else None,
                        'resolucion': cell_texts[2] if len(cell_texts) > 2 else None,
                        'fecha_novedad': cell_texts[3] if len(cell_texts) > 3 else None,
                    }
                    logger.info("Extracted cancelled cedula data: %s", result['novedad'])
                    return result

            # Check for table with data (active cedula with voting location)
            table = page.locator(SELECTORS['results_table'])
            if table.count() > 0:
                rows = page.locator(SELECTORS['results_row'])
                if rows.count() > 0:
                    cells = rows.first.locator('td')
                    cell_texts = [cells.nth(i).text_content().strip()
                                 for i in range(cells.count())]

                    # For active cedula, table shows voting location info
                    result = {
                        'status': 'found',
                        'raw_data': cell_texts,
                    }

                    # Try to map to known fields based on number of columns
                    if len(cell_texts) >= 4:
                        # Typical: NUIP | DEPARTAMENTO | MUNICIPIO | PUESTO | DIRECCIÓN | MESA
                        result['departamento'] = cell_texts[1] if len(cell_texts) > 1 else None
                        result['municipio'] = cell_texts[2] if len(cell_texts) > 2 else None
                        result['puesto'] = cell_texts[3] if len(cell_texts) > 3 else None
                        result['direccion'] = cell_texts[4] if len(cell_texts) > 4 else None
                        result['mesa'] = cell_texts[5] if len(cell_texts) > 5 else None

                    logger.info("Extracted voting location data")
                    return result

            # No recognizable results
            logger.warning("No recognizable results found on page")
            return {'status': 'parse_error', 'error': 'No recognizable results on page'}

        except PlaywrightTimeoutError:
            logger.warning("Results did not appear in time")
            return {'status': 'parse_error', 'error': 'Results timeout'}
        except Exception as e:
            logger.error("Failed to extract results: %s", str(e))
            return {'status': 'parse_error', 'error': str(e)}

    def scrape_cedula(self, cedula: str) -> dict:
        """
        Scrape census data for a given cedula.

        Flow:
        1. Navigate to page and wait for it to be ready
        2. Fill cedula input
        3. Solve reCAPTCHA using 2captcha
        4. Inject token and submit form
        5. Extract results from table

        Args:
            cedula: Colombian cedula number (6-10 digits)

        Returns:
            dict: Result with 'status' key and data fields.
                  Status codes: found, cancelled, not_found, captcha_failed,
                  timeout, network_error, parse_error
        """
        self._enforce_rate_limit()

        browser = self.get_browser()
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = None

        try:
            page = context.new_page()
            page.set_default_timeout(DEFAULT_TIMEOUT)

            # Step 1: Navigate and wait for page ready
            logger.info("Navigating to Registraduria for cedula=%s", cedula)
            page.goto(REGISTRADURIA_URL, timeout=PAGE_LOAD_TIMEOUT)
            self._wait_for_page_ready(page)

            # Step 2: Fill cedula input
            cedula_input = page.locator(SELECTORS['cedula_input']).first
            cedula_input.fill(cedula)
            logger.debug("Filled cedula input")

            # Small delay to let any validation run
            page.wait_for_timeout(500)

            # Step 3: Solve reCAPTCHA
            token = self._solve_recaptcha(page, REGISTRADURIA_URL)
            if not token:
                logger.error("Failed to solve reCAPTCHA for cedula=%s", cedula)
                return {'status': 'captcha_failed', 'error': 'Could not solve reCAPTCHA'}

            # Step 4: Inject token
            if not self._inject_captcha_token(page, token):
                return {'status': 'captcha_failed', 'error': 'Could not inject reCAPTCHA token'}

            # Small delay after token injection
            page.wait_for_timeout(1000)

            # Step 5: Click submit button
            submit = page.locator(SELECTORS['submit_button']).first
            submit.click()
            logger.debug("Clicked submit button")

            # Step 6: Wait for and extract results
            page.wait_for_timeout(2000)  # Give time for results to load
            result = self._extract_results_from_table(page)
            logger.info("Scrape %s: %s", cedula, result['status'])
            return result

        except PlaywrightTimeoutError as e:
            logger.error("Scrape %s: timeout - %s", cedula, str(e))
            return {'status': 'timeout', 'error': str(e)}

        except Exception as e:
            error_msg = str(e)
            logger.error("Scrape %s: network_error - %s", cedula, error_msg)

            # Try to capture screenshot for debugging if page exists
            if page and settings.DEBUG:
                try:
                    page.screenshot(path=f'/tmp/scraper_error_{cedula}.png')
                    logger.debug("Error screenshot saved to /tmp/scraper_error_%s.png", cedula)
                except Exception:
                    pass

            return {'status': 'network_error', 'error': error_msg}

        finally:
            context.close()
