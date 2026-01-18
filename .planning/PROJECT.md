# ___

## What This Is

A Django-based user portal with authentication. External users can register with their Colombian cédula, phone number, and personal details, then log in to access protected pages. This is the foundation for a larger application — all routes require authentication, with a clean login/register flow as the entry point.

## Core Value

Users can securely register and authenticate to access the portal. If authentication doesn't work reliably and securely, nothing else matters.

## Requirements

### Validated

- ✓ Django project scaffold — existing
- ✓ WSGI/ASGI entry points configured — existing

### Active

- [ ] All unauthenticated requests redirect to login page
- [ ] User registration with: Nombre Completo, Cédula (Colombian format validated), Phone, data policy acceptance
- [ ] User can log in with username and password
- [ ] "Remember me" option for extended sessions
- [ ] User can log in immediately after registration
- [ ] Home page displays after successful login with logout button
- [ ] Environment-based SECRET_KEY (.env file)
- [ ] .gitignore for Python/Django project

### Out of Scope

- OAuth/social login — adds complexity, not needed for v1
- Email verification — can add later if needed
- Password reset via email — can add later
- 2FA/MFA — defer to future version
- User profile editing — v1 is just auth flow
- Admin dashboard customization — Django admin is sufficient
- PostgreSQL — SQLite sufficient for small scale, defer to production setup
- Cloud deployment configuration — handle after local development complete

## Context

**Technical environment:**
- Django 5.x (note: requirements.txt needs correction)
- Python 3.14
- Existing project scaffold with name "___"
- Virtual environment in `.venv/`
- No apps created yet, just Django project structure
- SQLite database for development and initial deployment

**User context:**
- External/public users registering
- Small scale (<100 users)
- Colombian users (cédula validation for Colombia)

**Security context:**
- Storing PII (cédula, phone, name) — requires proper data handling
- Data policy acceptance required at registration
- Standard password requirements (Django defaults)

## Constraints

- **Tech stack**: Django + SQLite — minimal infrastructure
- **Deployment**: Local first, production infrastructure later
- **Project name**: Keep as `___`
- **Cédula format**: Colombian cédula de ciudadanía (6-10 digits)
- **Existing code**: Must work with current `___/` project structure
- **Cost**: Minimize infrastructure costs

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Django over alternatives | Built-in auth, secure defaults, good for expansion | — Pending |
| Extended User model | Custom fields (cedula, phone) needed | — Pending |
| SQLite for now | Sufficient for <100 users, minimal setup | — Pending |
| Login-required middleware | Cleaner than decorating every view | — Pending |
| Local-first development | Ship working product before production infrastructure | — Pending |

---
*Last updated: 2026-01-18 after requirements simplification*
