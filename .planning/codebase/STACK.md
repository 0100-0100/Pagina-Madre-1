# Technology Stack

**Analysis Date:** 2026-01-16

## Languages

**Primary:**
- Python 3.14.2 - Backend web application

## Runtime

**Environment:**
- Python 3.14.2

**Package Manager:**
- pip 25.3
- Lockfile: missing (requirements.txt present, no lock file)

## Frameworks

**Core:**
- Django 6.0.1 - Web framework

**Testing:**
- Not detected

**Build/Dev:**
- Django development server (built-in)

## Key Dependencies

**Critical:**
- Django 6.0.1 - Web framework providing MVC pattern, ORM, admin interface, authentication

**Infrastructure:**
- asgiref 3.11.0 - ASGI server reference implementation (Django async support)
- sqlparse 0.5.5 - SQL parsing library (used by Django for query formatting)

## Configuration

**Environment:**
- Configuration in `___/___/settings.py`
- Hardcoded SECRET_KEY (insecure development key)
- DEBUG mode enabled
- No .env file detected
- Settings module: `___.settings`

**Build:**
- No build configuration detected (pure Python)
- Virtual environment in `.venv/`

## Platform Requirements

**Development:**
- Python 3.14+
- Virtual environment recommended (`.venv/` present)

**Production:**
- WSGI server support via `___/___/wsgi.py`
- ASGI server support via `___/___/asgi.py`
- Database: SQLite3 (development) - requires migration for production
- Deployment target: Not configured

---

*Stack analysis: 2026-01-16*
