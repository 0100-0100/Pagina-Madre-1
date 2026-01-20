"""
Registraduria Census Data Scraper

This module provides a headless browser scraper for retrieving electoral
census data from Colombia's Registraduria. It uses Playwright to navigate
the census lookup page and extract voting location information.

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
    - 'not_found': Cedula not in census
    - 'cancelled': Cedula cancelled (deceased or other)
    - 'blocked': F5 CSPM bot detection triggered
    - 'timeout': Registraduria server timeout
    - 'network_error': Connection failed
    - 'parse_error': HTML structure changed
"""

import logging
import time

from django.conf import settings
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


# Constants
REGISTRADURIA_URL = 'https://consultacenso.registraduria.gov.co/consultar/'
DEFAULT_TIMEOUT = 90000  # 90 seconds in milliseconds
RATE_LIMIT_SECONDS = 5  # Minimum seconds between requests
PAGE_LOAD_TIMEOUT = 30000  # 30 seconds for initial page load

# CSS Selectors for Registraduria page elements
# These may need adjustment if the site structure changes
SELECTORS = {
    # Form elements
    'cedula_input': 'input#cedula, input[name="cedula"], input[type="text"]',
    'submit_button': 'button:has-text("Consultar"), input[type="submit"]',
    # Result detection
    'result_area': '#resultado, .resultado, .contenido-resultado',
    'error_message': '.mensaje-error, .error, .alert-danger',
    # Active cedula - voting location fields
    'departamento': '#departamento, .departamento, td:has-text("Departamento") + td',
    'municipio': '#municipio, .municipio, td:has-text("Municipio") + td',
    'puesto': '#puesto, .puesto, td:has-text("Puesto") + td',
    'direccion': '#direccion, .direccion, td:has-text("Direcci") + td',
    'mesa': '#mesa, .mesa, td:has-text("Mesa") + td',
    # Cancelled cedula fields
    'novedad': '#novedad, .novedad, td:has-text("Novedad") + td',
    'resolucion': '#resolucion, .resolucion, td:has-text("Resoluci") + td',
    'fecha_novedad': '#fecha_novedad, .fecha-novedad, td:has-text("Fecha") + td',
}

# Text patterns for detecting response types
PATTERNS = {
    'active': ['LUGAR DE VOTACION', 'INFORMACION DEL LUGAR', 'PUESTO DE VOTACION'],
    'cancelled': ['NOVEDAD', 'CANCELADA', 'FALLECIDO', 'RESOLUCION'],
    'not_found': ['NO SE ENCUENTRA', 'NO ENCONTRADO', 'NO APARECE', 'NO EXISTE'],
    'blocked': ['ACCESS DENIED', 'ACCESO DENEGADO', 'BLOCKED', 'CHALLENGE'],
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
    """

    _playwright = None
    _browser = None

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

    def _extract_field(self, page, selector: str) -> str | None:
        """
        Extract text from a page element by selector.

        Args:
            page: Playwright page object
            selector: CSS selector string

        Returns:
            Stripped text content or None if element not found
        """
        try:
            locator = page.locator(selector)
            if locator.count() > 0:
                text = locator.first.text_content()
                return text.strip() if text else None
        except Exception:
            pass
        return None

    def _detect_response_type(self, page) -> str:
        """
        Detect the type of response from the Registraduria page.

        Analyzes page content to determine if cedula was found,
        not found, cancelled, or if access was blocked.

        Args:
            page: Playwright page object after form submission

        Returns:
            Response type: 'found', 'not_found', 'cancelled', or 'blocked'
        """
        content = page.content().upper()

        # Check for blocked/challenge page first (highest priority)
        for pattern in PATTERNS['blocked']:
            if pattern in content:
                return 'blocked'

        # Check for active cedula with voting location
        for pattern in PATTERNS['active']:
            if pattern in content:
                return 'found'

        # Check for cancelled cedula
        for pattern in PATTERNS['cancelled']:
            if pattern in content:
                return 'cancelled'

        # Check for not found
        for pattern in PATTERNS['not_found']:
            if pattern in content:
                return 'not_found'

        # Unable to determine - likely parse error
        return 'unknown'

    def _extract_active_data(self, page) -> dict:
        """
        Extract voting location data for an active cedula.

        Args:
            page: Playwright page object with active cedula result

        Returns:
            dict with status='found' and voting location fields
        """
        return {
            'status': 'found',
            'departamento': self._extract_field(page, SELECTORS['departamento']),
            'municipio': self._extract_field(page, SELECTORS['municipio']),
            'puesto': self._extract_field(page, SELECTORS['puesto']),
            'direccion': self._extract_field(page, SELECTORS['direccion']),
            'mesa': self._extract_field(page, SELECTORS['mesa']),
        }

    def _extract_cancelled_data(self, page) -> dict:
        """
        Extract cancellation data for a cancelled cedula.

        Args:
            page: Playwright page object with cancelled cedula result

        Returns:
            dict with status='cancelled' and cancellation fields
        """
        return {
            'status': 'cancelled',
            'novedad': self._extract_field(page, SELECTORS['novedad']),
            'resolucion': self._extract_field(page, SELECTORS['resolucion']),
            'fecha_novedad': self._extract_field(page, SELECTORS['fecha_novedad']),
        }

    def scrape_cedula(self, cedula: str) -> dict:
        """
        Scrape census data for a given cedula.

        Creates a fresh browser context for isolation, performs
        the scrape, and ensures context cleanup in finally block.

        Args:
            cedula: Colombian cedula number (6-10 digits)

        Returns:
            dict: Result with 'status' key and data fields.
                  Status codes: found, not_found, cancelled, blocked,
                  timeout, network_error, parse_error
        """
        browser = self.get_browser()
        context = browser.new_context()
        page = None
        try:
            page = context.new_page()
            page.set_default_timeout(DEFAULT_TIMEOUT)

            # Navigate to page
            logger.debug("Navigating to %s for cedula=%s", REGISTRADURIA_URL, cedula)
            page.goto(REGISTRADURIA_URL, timeout=PAGE_LOAD_TIMEOUT,
                     wait_until='domcontentloaded')

            # Fill and submit form
            cedula_input = page.locator(SELECTORS['cedula_input'])
            cedula_input.fill(cedula)

            submit_button = page.locator(SELECTORS['submit_button'])
            submit_button.click()

            # Wait for result to appear
            result_locator = page.locator(
                f"{SELECTORS['result_area']}, {SELECTORS['error_message']}"
            )
            result_locator.wait_for(state='visible', timeout=DEFAULT_TIMEOUT)

            # Detect response type and extract data
            response_type = self._detect_response_type(page)

            if response_type == 'found':
                result = self._extract_active_data(page)
                logger.info("Scrape %s: %s", cedula, result['status'])
                logger.debug("Extracted data for %s: %s", cedula, result)
                return result

            elif response_type == 'cancelled':
                result = self._extract_cancelled_data(page)
                logger.info("Scrape %s: %s", cedula, result['status'])
                logger.debug("Extracted data for %s: %s", cedula, result)
                return result

            elif response_type == 'not_found':
                logger.info("Scrape %s: not_found", cedula)
                return {'status': 'not_found'}

            elif response_type == 'blocked':
                raw_html = page.content()
                logger.warning("Scrape %s: blocked - F5 CSPM challenge detected", cedula)
                return {
                    'status': 'blocked',
                    'raw_html': raw_html,
                    'error': 'F5 CSPM challenge detected'
                }

            else:
                # Unknown response type - likely parse error
                raw_html = page.content()
                logger.error("Scrape %s: parse_error - unknown response type", cedula)
                return {
                    'status': 'parse_error',
                    'raw_html': raw_html,
                    'error': 'Unable to determine response type'
                }

        except PlaywrightTimeoutError as e:
            logger.error("Scrape %s: timeout - %s", cedula, str(e))
            return {'status': 'timeout', 'error': str(e)}

        except Exception as e:
            # Catch-all for network and other errors
            error_msg = str(e)
            logger.error("Scrape %s: network_error - %s", cedula, error_msg)

            # Try to capture raw HTML for debugging if page exists
            raw_html = None
            if page:
                try:
                    raw_html = page.content()
                except Exception:
                    pass

            result = {'status': 'network_error', 'error': error_msg}
            if raw_html:
                result['raw_html'] = raw_html
            return result

        finally:
            context.close()
