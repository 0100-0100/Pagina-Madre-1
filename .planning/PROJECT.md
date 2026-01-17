# ___ (User Portal)

## What This Is

A Django-based user portal with protected authentication for external users. All unauthenticated requests redirect to login. Users can register with Colombian cédula validation, then access a home page that serves as the entry point for future features.

## Core Value

Users can securely register and authenticate with validated identity information (cédula), ensuring only verified users access the protected application.

## Requirements

### Validated

- ✓ Django project scaffold exists — existing
- ✓ WSGI/ASGI entry points configured — existing
- ✓ Admin interface available at /admin/ — existing

### Active

- [ ] All unauthenticated GET requests redirect to login page
- [ ] Login page with email/username and password
- [ ] Registration page with: Nombre Completo, Cédula (Colombian format), Phone, Password, Data policy checkbox
- [ ] Colombian cédula format validation (6-10 digits)
- [ ] Data policy acceptance checkbox (required, links to policy page)
- [ ] User model extended with custom fields (nombre_completo, cedula, phone, policy_accepted)
- [ ] Successful registration allows immediate login
- [ ] Home page (protected) with welcome message and logout button
- [ ] Logout functionality returns user to login page
- [ ] Django default password validation (min 8 chars, not common, not all numeric)
- [ ] CSRF protection on all forms
- [ ] Secure session handling

### Out of Scope

- Email verification on registration — adds complexity, not needed for <100 users initially
- Password reset via email — can add in v2
- OAuth/social login — email/password sufficient for v1
- Two-factor authentication — defer to v2
- User profile editing after registration — defer to v2
- Admin user management UI — Django admin sufficient
- Mobile app — web only
- API endpoints — server-rendered templates for v1

## Context

**Existing codebase:**
- Django 6.0.1 project with placeholder name "___"
- Fresh scaffold with no apps, models, or templates created
- SQLite database for development
- Virtual environment in `.venv/`
- Security concerns identified: hardcoded SECRET_KEY, DEBUG=True, no .gitignore

**Target users:**
- External/public users (not internal team)
- Small scale: <100 users expected
- Colombian users requiring cédula de ciudadanía

**Growth path:**
- This is v1/entry point for a larger application
- Designed to expand with additional features after authentication is solid

## Constraints

- **Tech stack**: Django (already scaffolded, good fit for auth + expansion)
- **Database**: PostgreSQL for production (SQLite for dev)
- **Deployment**: AWS (specific service TBD — likely Elastic Beanstalk or ECS)
- **Security**: Production-ready auth from day one (external users with PII)
- **Validation**: Colombian cédula format (6-10 digits)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Keep Django over alternatives | Built-in auth, easy to extend, good for "expand later" | — Pending |
| Extend Django User model | Need custom fields (cedula, phone, nombre_completo) | — Pending |
| Server-rendered templates | Simpler than SPA for auth flow, fewer moving parts | — Pending |
| PostgreSQL for production | SQLite unsuitable for concurrent users, AWS RDS available | — Pending |
| Environment-based config | Secrets must not be in code, different envs need different values | — Pending |

---
*Last updated: 2026-01-17 after initialization*
