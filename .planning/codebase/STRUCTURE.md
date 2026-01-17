# Codebase Structure

**Analysis Date:** 2026-01-16

## Directory Layout

```
Pagina-Madre-1/
├── ___/                     # Django project root
│   ├── ___/                 # Project configuration package
│   │   ├── __init__.py      # Package marker
│   │   ├── asgi.py          # ASGI application entry
│   │   ├── settings.py      # Django settings
│   │   ├── urls.py          # Root URL configuration
│   │   └── wsgi.py          # WSGI application entry
│   └── manage.py            # Django management script
├── .venv/                   # Python virtual environment
├── .planning/               # GSD planning documents
│   └── codebase/            # Codebase analysis documents
├── requirements.txt         # Python dependencies
└── README.md                # Project readme
```

## Directory Purposes

**`___/` (Project Root):**
- Purpose: Django project container
- Contains: Django apps, manage.py, project configuration
- Key files: `manage.py`

**`___/___/` (Configuration Package):**
- Purpose: Core Django project configuration
- Contains: Settings, URL routing, WSGI/ASGI configs
- Key files: `settings.py`, `urls.py`, `wsgi.py`, `asgi.py`

**`.venv/`:**
- Purpose: Isolated Python virtual environment
- Contains: Installed packages (Django 6.0.1, dependencies)
- Generated: Yes (by python -m venv)
- Committed: No

**`.planning/`:**
- Purpose: GSD command planning and codebase documentation
- Contains: Phase plans, codebase analysis documents
- Generated: Yes (by GSD commands)
- Committed: Yes

**`.planning/codebase/`:**
- Purpose: Codebase mapping documents
- Contains: ARCHITECTURE.md, STRUCTURE.md, etc.
- Generated: Yes (by /gsd:map-codebase)
- Committed: Yes

## Key File Locations

**Entry Points:**
- `___/manage.py`: CLI management interface
- `___/___/wsgi.py`: WSGI server entry point
- `___/___/asgi.py`: ASGI server entry point

**Configuration:**
- `___/___/settings.py`: Django settings (database, middleware, apps, etc.)
- `___/___/urls.py`: Root URL patterns
- `requirements.txt`: Python package dependencies

**Core Logic:**
- Not yet implemented (no Django apps created)

**Testing:**
- Not yet implemented (no test files present)

## Naming Conventions

**Files:**
- Django convention: `settings.py`, `urls.py`, `wsgi.py`, `asgi.py`, `manage.py`
- Configuration: lowercase with underscores (Python module style)

**Directories:**
- Project name: `___` (placeholder, should be renamed to actual project name)
- Django apps: Not yet created (typically lowercase, no spaces)

**Python Modules:**
- Package markers: `__init__.py`
- Entry points: `manage.py`, `wsgi.py`, `asgi.py`

## Where to Add New Code

**New Django App:**
- Create app: `python ___/manage.py startapp app_name`
- Location: `___/app_name/`
- Register in: `___/___/settings.py` INSTALLED_APPS list
- URL routing: Include app URLs in `___/___/urls.py`

**New Feature:**
- Primary code: `___/app_name/views.py` (view functions/classes)
- Models: `___/app_name/models.py` (database models)
- URLs: `___/app_name/urls.py` (app-specific URL patterns)
- Templates: `___/app_name/templates/app_name/` (HTML templates)
- Static files: `___/app_name/static/app_name/` (CSS, JS, images)
- Tests: `___/app_name/tests.py` or `___/app_name/tests/`

**New Model:**
- Implementation: `___/app_name/models.py`
- Register admin: `___/app_name/admin.py`
- Migrations: Generated via `python ___/manage.py makemigrations`

**New View:**
- Implementation: `___/app_name/views.py`
- URL mapping: `___/app_name/urls.py`
- Template: `___/app_name/templates/app_name/template_name.html`

**New URL Pattern:**
- App-level: `___/app_name/urls.py`
- Project-level: `___/___/urls.py` (include app URLs)

**Utilities:**
- Shared helpers: `___/app_name/utils.py` or `___/common/utils.py`
- Custom middleware: `___/app_name/middleware.py`
- Custom management commands: `___/app_name/management/commands/command_name.py`

**Templates:**
- App templates: `___/app_name/templates/app_name/`
- Shared templates: `___/templates/` (create directory, add to settings.TEMPLATES DIRS)

**Static Files:**
- App static: `___/app_name/static/app_name/`
- Shared static: `___/static/` (create directory, configure STATICFILES_DIRS)

## Special Directories

**`.venv/`:**
- Purpose: Python virtual environment with isolated dependencies
- Generated: Yes (by `python -m venv .venv`)
- Committed: No (excluded via .gitignore)

**`.planning/`:**
- Purpose: GSD planning workspace
- Generated: Yes (by GSD commands)
- Committed: Yes

**Database:**
- File: `___/db.sqlite3` (not yet created, will be generated on first migration)
- Generated: Yes (by `python ___/manage.py migrate`)
- Committed: No (should be excluded for development databases)

**Migrations:**
- Location: `___/app_name/migrations/` (per-app, not yet created)
- Generated: Yes (by `python ___/manage.py makemigrations`)
- Committed: Yes (migration files track schema changes)

**Media Files:**
- Location: Not yet configured (typically `___/media/`)
- Purpose: User-uploaded files
- Committed: No (should be excluded, served separately in production)

---

*Structure analysis: 2026-01-16*
