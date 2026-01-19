# Project State

## Project Reference

See: .planning/PROJECT.md

**Core value:** Users can securely register and authenticate to access the portal. If authentication doesn't work reliably and securely, nothing else matters.
**Current focus:** Phase 3 — Protected Portal

## Current Position

Phase: 3 of 3 (Protected Portal)
Plan: Ready to plan
Status: Phase 2 complete, ready for Phase 3
Last activity: 2026-01-19 — Phase 2 verified and complete

Progress: ██████░░░░ 66%

## Performance Metrics

**Velocity:**
- Total plans completed: 4
- Average duration: 3min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-foundation | 1/3 | 1min | 1min |
| 02-authentication-system | 3/3 | 11min | 4min |

## Accumulated Context

### Decisions

| Phase | Plan | Decision | Rationale |
|-------|------|----------|-----------|
| 01 | 01 | Use Django 4.2 LTS | Stability and long-term support vs non-existent 6.0.1 |
| 01 | 01 | Use python-decouple | Simpler than django-environ, sufficient for needs |
| 01 | 01 | Store SECRET_KEY in .env | Security - exclude from git, use .env.example as template |
| 02 | 01 | Use AbstractUser over AbstractBaseUser | Preserves Django's complete auth stack (username/password, admin, permissions) while adding custom fields. AbstractBaseUser would require 6-12 hours of custom implementation |
| 02 | 01 | Set AUTH_USER_MODEL before migrations | Critical timing requirement - must be configured before any auth migrations run to avoid costly schema fixes |
| 02 | 01 | Place accounts before django.contrib.auth in INSTALLED_APPS | Ensures CustomUser model loads before Django's auth system references it |
| 02 | 02 | Use cedula as username | Simplifies authentication with single identifier - users login with cedula instead of separate username |
| 02 | 02 | Remember me controls session duration | set_expiry(0) for browser close, set_expiry(1209600) for 14 days based on checkbox |
| 02 | 02 | Form validation delegates to model validators | DRY principle - avoid duplicate validation logic, single source of truth |
| 02 | 02 | Immediate login after registration | Improved UX - reduced friction, user doesn't need separate login step |
| 02 | 02 | Session security with HTTPONLY and SAMESITE | CSRF protection - prevents JavaScript access, restricts cross-site requests |
| 02 | 03 | Custom middleware over third-party package | Zero dependencies, ~30 lines of code, full control over exemptions |
| 02 | 03 | LoginRequired after AuthenticationMiddleware | LoginRequired needs request.user from AuthenticationMiddleware to check authentication |
| 02 | 03 | Use startswith() for URL exemptions | Covers sub-paths automatically (e.g., /admin/ matches /admin/login/) without enumerating every path |
| 02 | 03 | Exempt /static/ from authentication | Login and register pages need CSS/JS files to render correctly |

### Pending Todos

(None yet)

### Blockers/Concerns

(None yet)

## Session Continuity

Last session: 2026-01-19T14:32:18Z
Stopped at: Completed 02-03-PLAN.md (Phase 2 complete)
Resume file: None
