# Architecture

**Analysis Date:** 2026-01-16

## Pattern Overview

**Overall:** Model-View-Template (MVT) - Django Framework

**Key Characteristics:**
- Django 6.0.1 web framework following MVT pattern
- Fresh project scaffold with minimal customization
- SQLite database for development
- Monolithic application structure with placeholder project name "___"

## Layers

**Presentation Layer (Templates):**
- Purpose: Render HTML responses to users
- Location: `___/templates/` (not yet created)
- Contains: Django templates, static assets
- Depends on: Views layer
- Used by: End users via HTTP responses

**Business Logic Layer (Views):**
- Purpose: Handle HTTP requests and orchestrate responses
- Location: Django apps (not yet created)
- Contains: View functions/classes, form handlers
- Depends on: Models layer
- Used by: URL routing system

**Data Access Layer (Models):**
- Purpose: Define data structures and database interactions
- Location: Django apps `models.py` (not yet created)
- Contains: Django ORM models
- Depends on: Database backend
- Used by: Views layer

**URL Routing Layer:**
- Purpose: Map URL patterns to view functions
- Location: `___/___/urls.py`
- Contains: URL patterns using `django.urls.path`
- Depends on: Views layer
- Used by: Django request/response cycle

**Configuration Layer:**
- Purpose: Application settings and environment configuration
- Location: `___/___/settings.py`
- Contains: Django settings, middleware stack, installed apps
- Depends on: Nothing
- Used by: All layers

## Data Flow

**HTTP Request Flow:**

1. Request arrives at WSGI/ASGI application (`wsgi.py` or `asgi.py`)
2. Django middleware processes request (security, sessions, CSRF, auth, messages)
3. URL dispatcher matches pattern in `___.urls` and routes to view
4. View processes request, queries models if needed
5. View returns response (template render or data)
6. Middleware processes response
7. Response sent to client

**State Management:**
- Session data: Django session framework with database backend
- Authentication: Django contrib.auth with database-backed user models
- Messages: Django contrib.messages framework

## Key Abstractions

**WSGI/ASGI Applications:**
- Purpose: Server interface for HTTP requests
- Examples: `___/___/wsgi.py`, `___/___/asgi.py`
- Pattern: Callable that exposes Django application to WSGI/ASGI servers

**Settings Module:**
- Purpose: Centralized configuration
- Examples: `___/___/settings.py`
- Pattern: Python module with uppercase variables for settings

**URL Configuration:**
- Purpose: URL routing and view mapping
- Examples: `___/___/urls.py`
- Pattern: List of `path()` patterns in `urlpatterns`

**Management Commands:**
- Purpose: CLI utility for administrative tasks
- Examples: `___/manage.py`
- Pattern: Django management command framework

## Entry Points

**Development Server:**
- Location: `___/manage.py`
- Triggers: `python manage.py runserver`
- Responsibilities: CLI entry for Django management commands (migrations, shell, server, etc.)

**WSGI Production Server:**
- Location: `___/___/wsgi.py`
- Triggers: WSGI server (Gunicorn, uWSGI, etc.)
- Responsibilities: Synchronous HTTP request handling

**ASGI Production Server:**
- Location: `___/___/asgi.py`
- Triggers: ASGI server (Daphne, Uvicorn, etc.)
- Responsibilities: Asynchronous HTTP/WebSocket request handling

**Admin Interface:**
- Location: `path('admin/', admin.site.urls)` in `___/___/urls.py`
- Triggers: `/admin/` URL path
- Responsibilities: Django admin interface for model management

## Error Handling

**Strategy:** Django's built-in exception handling with middleware support

**Patterns:**
- Development: DEBUG=True shows detailed error pages with stack traces
- Production: DEBUG=False shows generic error pages, logs to configured handlers
- HTTP exceptions use Django's built-in error views (404, 500, 403, 400)

## Cross-Cutting Concerns

**Logging:** Django logging framework (not yet configured beyond defaults)

**Validation:** Django forms and model field validation (no custom validators yet)

**Authentication:** Django contrib.auth with middleware-based session authentication

**Security:**
- SecurityMiddleware for HTTPS redirect and security headers
- CSRF protection via CsrfViewMiddleware
- XFrameOptionsMiddleware for clickjacking protection
- Secret key for cryptographic signing (currently using development key)

---

*Architecture analysis: 2026-01-16*
