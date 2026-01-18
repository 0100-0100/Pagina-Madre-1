# ___

## What This Is

A Django-based authentication portal for external users. Users must register with their Colombian cédula, phone number, and accept data policies before accessing the application. This is the foundation for a larger application — starting with secure, validated user authentication.

## Core Value

Users can securely register and authenticate with validated Colombian identity information before accessing protected content.

## Requirements

### Validated

- ✓ Django project scaffold — existing
- ✓ Codebase mapped — existing

### Active

- [ ] All unauthenticated GET requests redirect to login page
- [ ] Login page with email/username and password authentication
- [ ] Registration page with: Nombre Completo, Cédula, Phone, Password, Data policy checkbox
- [ ] Colombian cédula validation (6-10 digit format)
- [ ] Colombian phone validation (+57 mobile format)
- [ ] Data policy acceptance checkbox (required, placeholder text for now)
- [ ] User saved to database on registration, can login immediately
- [ ] Home page after login with logout button
- [ ] Logout redirects back to login page
- [ ] Secure session management (CSRF, secure cookies, password hashing)
- [ ] Environment-based configuration (secrets not in code)
- [ ] Production-ready database configuration (PostgreSQL)

### Out of Scope

- Email verification — not needed for v1, can add later
- Password reset flow — deferred to v2
- OAuth/social login — unnecessary complexity for v1
- Two-factor authentication — deferred to v2
- User profile editing — v2 feature
- Admin dashboard customization — Django admin sufficient for now

## Context

**Existing codebase:** Django 6.0.1 project with placeholder name "___". Fresh scaffold with no apps, no custom models, no tests. Security concerns identified: hardcoded SECRET_KEY, DEBUG=True, missing .gitignore.

**Target users:** External/public users (Colombian citizens). Small scale initially (<100 users), but architecture should support growth.

**Deployment target:** AWS (specific service TBD — likely Elastic Beanstalk or ECS).

**Validation requirements:**
- Colombian cédula: 6-10 numeric digits
- Colombian phone: +57 followed by 10 digits (mobile starts with 3)

## Constraints

- **Tech stack**: Django 5.x (fix version in requirements.txt — 6.x doesn't exist)
- **Database**: PostgreSQL for production, SQLite acceptable for local dev
- **Security**: Must use environment variables for secrets, no hardcoded credentials
- **Language**: Spanish UI (field labels, error messages, buttons)
- **Compatibility**: Modern browsers, mobile-responsive

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Keep project name "___" | User preference despite unconventional naming | — Pending |
| Django over alternatives | Built-in auth, batteries included, good for expansion | — Pending |
| Custom User model | Need extra fields (cedula, phone, full_name) | — Pending |
| Session-based auth | Simpler than JWT for server-rendered pages | — Pending |
| PostgreSQL for production | Robust, AWS RDS support, better than SQLite | — Pending |

---
*Last updated: 2026-01-18 after initialization*
