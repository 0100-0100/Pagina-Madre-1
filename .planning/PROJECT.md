# ___

## What This Is

A Django-based authentication portal for Colombian users with professional Bootstrap 5 styling and automated cédula validation. External users can register with their cédula (6-10 digits validated), phone number, and personal details, then log in to access protected pages. The system auto-validates cédulas against Registraduría's electoral census via background tasks, displays voting location data, and provides leaders with bulk refresh capabilities for their referrals.

## Core Value

Users can securely register and authenticate to access the portal. If authentication doesn't work reliably and securely, nothing else matters.

## Current State

**Shipped:** v1.3 Async Background Jobs (2026-01-22)

**Tech stack:**
- Django 4.2 LTS
- Python 3.14
- SQLite database with WAL mode
- Django-Q2 background task queue
- Playwright headless browser + 2captcha
- python-decouple for environment variables
- Bootstrap 5.3.8 via jsDelivr CDN
- HTMX 2.0.4 for dynamic updates

**Codebase:**
- ~4,300 lines of code (Python + HTML)
- 9 HTML templates + 3 partials
- Custom User model with cédula validation, referral tracking, and role field
- CedulaInfo model with 9 status choices for census data
- Global login-required middleware
- Real-time form validation with input filtering
- Background task processing with exponential backoff retry
- Leader RBAC for census refresh capabilities

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
- ✓ Bootstrap 5 CSS framework integrated via CDN (jsDelivr with SRI) — v1.1
- ✓ Base template with Bootstrap includes for all pages — v1.1
- ✓ Login page styled with Bootstrap card, real-time validation — v1.1
- ✓ Register page styled with Bootstrap card, input filtering — v1.1
- ✓ Home page styled with navbar and user info display — v1.1
- ✓ Responsive design (mobile-friendly) across all pages — v1.1
- ✓ Real-time form validation with debounce (1.5s delay) — v1.1
- ✓ Input filtering: numeric-only for cédula/phone, letters+accents for nombre — v1.1
- ✓ Django messages displayed as Bootstrap alerts — v1.1
- ✓ Form widget classes applied in forms.py — v1.1
- ✓ Referral link generation (unique per user, embedded in registration URL) — v1.2
- ✓ Registration captures referrer from URL parameter — v1.2
- ✓ Referrer-referred relationship stored in database — v1.2
- ✓ Home page displays referral count and progress toward goal — v1.2
- ✓ Home page shows shareable referral link — v1.2
- ✓ Profile page for editing nombre, teléfono, password — v1.2
- ✓ Profile page for setting/updating referral goal — v1.2
- ✓ Referidos page with table (Nombre, Cédula, Teléfono, Fecha de registro) — v1.2
- ✓ Navigation links from home to Perfil and Referidos pages — v1.2
- ✓ Background task queue system (Django-Q2 with ORM broker) — v1.3
- ✓ Playwright-based scraper for Registraduría census lookup — v1.3
- ✓ CedulaInfo model to store voting/census data (9 status choices) — v1.3
- ✓ Auto-trigger validation after user registration (post_save signal) — v1.3
- ✓ Manual refresh option for census data (leader RBAC) — v1.3
- ✓ Handle all response types (active, cancelled, not found, error) — v1.3
- ✓ HTMX-powered status display with conditional polling — v1.3
- ✓ Leader bulk refresh for referrals (max 10, 30-second cooldown) — v1.3

### Active

(None — ready for v1.4 planning)

### Out of Scope

- OAuth/social login — adds complexity, not needed
- Email verification — can add later if needed
- Password reset via email — can add later
- 2FA/MFA — defer to future version
- Admin dashboard customization — Django admin is sufficient
- PostgreSQL — SQLite sufficient for small scale, defer to production setup
- Cloud deployment configuration — handle after local development complete
- Custom CSS/design system — using Bootstrap 5 for simplicity
- Local Bootstrap files — CDN is acceptable for now
- Referral rewards/incentives — goal is tracking only, no rewards system

## Context

**User context:**
- External/public users registering
- Small scale (<100 users)
- Colombian users (cédula validation for Colombia)
- Leaders can view and refresh census data for their referrals

**Security context:**
- Storing PII (cédula, phone, name) — requires proper data handling
- Data policy acceptance required at registration
- Session security: HTTPONLY, SAMESITE cookies
- CSRF protection on all forms
- RBAC: USER vs LEADER roles (superadmin-only role assignment)

**UI context:**
- Bootstrap 5 styling complete on all pages
- Spanish language labels throughout
- 9 templates + 3 partials
- Real-time form validation with input filtering
- Bootstrap Icons for navigation
- HTMX for dynamic census status updates

## Constraints

- **Tech stack**: Django + SQLite + Bootstrap 5 CDN
- **Deployment**: Local first, production infrastructure later
- **Project name**: Keep as `___`
- **Cédula format**: Colombian cédula de ciudadanía (6-10 digits)
- **Existing code**: Must work with current `___/` project structure
- **Cost**: Minimize infrastructure costs
- **Existing functionality**: Keep existing auth functionality intact

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
| Bootstrap 5.3.8 via jsDelivr CDN | Quick setup, SRI integrity, no build step | ✓ Good |
| Real-time validation with 1.5s debounce | Responsive UX without excessive server calls | ✓ Good |
| Input filtering (block invalid chars) | Better UX than post-validation errors | ✓ Good |
| Navbar in home.html only | Avoid showing nav on auth pages | ✓ Good |
| Server-side validation mirrors client-side | Security backup for form validation | ✓ Good |
| Three-step migration for unique fields | Add nullable, populate, add constraint — SQLite safe | ✓ Good |
| Self-referential ForeignKey with SET_NULL | Preserves user when referrer deleted | ✓ Good |
| filter().first() for referral lookup | Graceful handling of invalid codes | ✓ Good |
| Django PasswordChangeView extension | Secure password handling with session preservation | ✓ Good |
| navigator.clipboard API | Modern clipboard access with fallback | ✓ Good |
| ORM broker with SQLite for Django-Q2 | <100 users scenario, no Redis needed | ✓ Good |
| Single worker (workers=1) | Critical for SQLite write safety | ✓ Good |
| WAL mode via connection_created signal | Enables concurrent web + qcluster access | ✓ Good |
| Browser singleton with context isolation | Performance + clean state per scrape | ✓ Good |
| 2captcha for reCAPTCHA | Fully automated census lookup | ✓ Good |
| dispatch_uid for signal deduplication | Prevents duplicate task queueing | ✓ Good |
| HTMX conditional polling | Stops on final states, reduces server load | ✓ Good |
| leader_or_self_required decorator | Self-access first, then role-based referral access | ✓ Good |
| 30-second server-side cooldown | Uses fetched_at timestamp, prevents refresh spam | ✓ Good |

## Workflow Conventions

### Milestone Completion Checklist

Before running `/gsd:complete-milestone`, always:

1. **Manual Bug Hunting** — Test all new features introduced in the milestone
   - Walk through each user-facing feature manually
   - Test edge cases and error states
   - Document any bugs found in BUGTRACKER.md
   - Fix all bugs before archiving milestone

2. **Run `/gsd:audit-milestone`** — Verify requirements satisfaction

3. **Then `/gsd:complete-milestone`** — Archive and prepare for next version

This ensures shipped milestones are production-ready, not just "code complete."

---
*Last updated: 2026-01-22 after v1.3 milestone*
