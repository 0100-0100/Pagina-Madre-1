# ___

## What This Is

A Django-based authentication portal for Colombian users. External users can register with their cédula (6-10 digits validated), phone number, and personal details, then log in to access protected pages. All routes require authentication, with a clean login/register flow as the entry point.

## Core Value

Users can securely register and authenticate to access the portal. If authentication doesn't work reliably and securely, nothing else matters.

## Current State

**Shipped:** v1.0 MVP (2026-01-19)

**Tech stack:**
- Django 4.2 LTS
- Python 3.14
- SQLite database
- python-decouple for environment variables

**Codebase:**
- 17 Python files, 459 LOC
- 3 HTML templates
- Custom User model with cedula validation
- Global login-required middleware

## Requirements

### Validated

- ✓ All unauthenticated requests redirect to login page — v1.0
- ✓ User registration with: Nombre Completo, Cédula (Colombian format validated), Phone, data policy acceptance — v1.0
- ✓ User can log in with cédula and password — v1.0
- ✓ "Remember me" option for extended sessions — v1.0
- ✓ User can log in immediately after registration — v1.0
- ✓ Home page displays after successful login with logout button — v1.0
- ✓ Environment-based SECRET_KEY (.env file) — v1.0
- ✓ .gitignore for Python/Django project — v1.0

### Active

(None yet — run `/gsd:define-requirements` for next milestone)

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

**User context:**
- External/public users registering
- Small scale (<100 users)
- Colombian users (cédula validation for Colombia)

**Security context:**
- Storing PII (cédula, phone, name) — requires proper data handling
- Data policy acceptance required at registration
- Session security: HTTPONLY, SAMESITE cookies
- CSRF protection on all forms

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
| Django 4.2 LTS over newer versions | Stability and long-term support | ✓ Good |
| AbstractUser over AbstractBaseUser | Preserves Django's complete auth stack while adding custom fields | ✓ Good |
| Cédula as username | Simplifies authentication — single identifier for login | ✓ Good |
| Custom middleware over third-party | Zero dependencies, ~30 lines, full control | ✓ Good |
| Remember me via session.set_expiry() | Flexible: 0 for browser close, 1209600 for 14 days | ✓ Good |
| SQLite for now | Sufficient for <100 users, minimal setup | ✓ Good |
| Local-first development | Ship working product before production infrastructure | ✓ Good |

---
*Last updated: 2026-01-19 after v1.0 milestone*
