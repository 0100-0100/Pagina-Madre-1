# External Integrations

**Analysis Date:** 2026-01-16

## APIs & External Services

**None detected:**
- No external API integrations found in codebase
- No third-party service SDKs installed

## Data Storage

**Databases:**
- SQLite3 (local file-based database)
  - Connection: Configured in `___/___/settings.py` (line 76-81)
  - Client: Django ORM (built-in)
  - Database file: `db.sqlite3` (not yet created)
  - Engine: `django.db.backends.sqlite3`

**File Storage:**
- Local filesystem only
  - Static files: `STATIC_URL = 'static/'` configured in `___/___/settings.py`
  - No cloud storage integration

**Caching:**
- None

## Authentication & Identity

**Auth Provider:**
- Django built-in authentication
  - Implementation: `django.contrib.auth` app (enabled in `___/___/settings.py` line 35)
  - Middleware: `django.contrib.auth.middleware.AuthenticationMiddleware` (line 47)
  - Password validators: 4 built-in validators configured (lines 87-100)
  - Admin interface: Available at `/admin/` route

## Monitoring & Observability

**Error Tracking:**
- None

**Logs:**
- Standard output only (no logging configuration detected)

## CI/CD & Deployment

**Hosting:**
- Not configured

**CI Pipeline:**
- None

## Environment Configuration

**Required env vars:**
- None currently required (all settings hardcoded in `___/___/settings.py`)

**Secrets location:**
- Hardcoded in settings file (insecure)
  - SECRET_KEY exposed in `___/___/settings.py` line 23

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

---

*Integration audit: 2026-01-16*
