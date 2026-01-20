# Phase 13: Playwright Scraper - Context

**Gathered:** 2026-01-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Headless browser scraper that retrieves census data from Registraduria's electoral census for any cedula. Returns structured data with voting location, handles various failure modes (not found, cancelled, blocked), and operates reliably in background tasks. Retry logic and task integration belong to Phase 14.

</domain>

<decisions>
## Implementation Decisions

### Response data structure
- Full extraction: all available fields (name, cedula status, department, municipality, voting place, voting address, voting table)
- Flat dict structure: `{'status': 'found', 'department': 'BOGOTA', 'municipality': '...', ...}`
- Store raw HTML only on error (not on success) — helps debug F5 blocks and parse failures
- Missing fields return None values — let calling code handle nulls

### Error handling & retries
- F5/bot detection: immediate failure with 'blocked' status — task layer handles retry
- Timeout: 90 seconds before giving up — Registraduria can be slow
- Network errors: return `{'status': 'network_error', 'error': '...'}` — no exceptions bubbling up
- Distinct statuses for 'not_found' vs 'parse_error' — helps identify when Registraduria changes their site structure

### Stealth configuration
- Minimal stealth for now: just headless emulation, no special patches
- Code structure should allow adding playwright-stealth and full stealth later if needed
- Browser mode: headless by default, headed when Django DEBUG=True
- Browser lifecycle: reuse browser instance with cookie/storage clearing between scrapes — faster than fresh instance
- Timing: wait for result element to appear (no fixed delays) — smarter and faster

### Logging & debugging
- Minimal production logging: only errors and final result status
- No screenshots on failure — simpler, less disk usage
- Use Django's logging system — integrates with existing config
- DEBUG log level shows extracted text, INFO shows just status

### Claude's Discretion
- Exact CSS selectors for Registraduria page elements
- Browser viewport dimensions
- Cookie clearing implementation details
- Element wait timeout values

</decisions>

<specifics>
## Specific Ideas

- "Let's prepare for full stealth in case we need to add it in a future milestone" — code structure should be modular
- Reuse browser for performance but ensure clean state between scrapes

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 13-playwright-scraper*
*Context gathered: 2026-01-20*
