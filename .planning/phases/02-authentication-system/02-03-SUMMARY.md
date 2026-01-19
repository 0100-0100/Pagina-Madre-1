---
phase: 02-authentication-system
plan: 03
subsystem: auth
tags: [django, middleware, authentication, login-required, global-auth]

# Dependency graph
requires:
  - phase: 02-02
    provides: Login and registration forms with cedula-based authentication
provides:
  - LoginRequiredMiddleware enforcing authentication globally
  - Redirect to login with ?next= parameter for post-login navigation
  - Exemptions for /login/, /register/, /admin/, /static/
affects: [03-landing-page, all future protected routes]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Custom middleware pattern for cross-cutting authentication concerns"
    - "Global authentication enforcement with selective exemptions"
    - "Post-login redirect via ?next= parameter"

key-files:
  created:
    - ___/middleware.py
  modified:
    - ___/___/settings.py

key-decisions:
  - "Custom middleware over third-party package - zero dependencies, ~30 lines of code"
  - "Middleware ordering critical - LoginRequired after AuthenticationMiddleware"
  - "Use startswith() for URL exemptions to cover sub-paths like /admin/login/"
  - "Exempt /static/ for login/register page CSS/JS without authentication"

patterns-established:
  - "Global middleware pattern: Cross-cutting concerns handled at middleware level"
  - "URL exemption pattern: startswith() matching for flexible path coverage"
  - "?next= parameter pattern: Preserve intended destination for post-login redirect"

# Metrics
duration: 1min
completed: 2026-01-19
---

# Phase 2 Plan 3: Login-Required Middleware Summary

**Global authentication enforcement via LoginRequiredMiddleware - redirects unauthenticated users to login with ?next= parameter, exempts /login/, /register/, /admin/, /static/**

## Performance

- **Duration:** 1 min
- **Started:** 2026-01-19T14:31:00Z
- **Completed:** 2026-01-19T14:32:18Z
- **Tasks:** 3 (2 implementation + 1 verification)
- **Files modified:** 2

## Accomplishments
- Created LoginRequiredMiddleware enforcing authentication across entire site
- All unauthenticated requests to protected URLs redirect to /login/?next=<path>
- Login, register, admin, and static file URLs accessible without authentication
- Middleware correctly ordered after AuthenticationMiddleware
- No redirect loops - exempted URLs work correctly

## Task Commits

Each task was committed atomically:

1. **Task 1: Create LoginRequiredMiddleware** - `c599443` (feat)
2. **Task 2: Configure middleware in settings** - `d583bb4` (feat)
3. **Task 3: Test middleware enforcement** - No commit (verification only)

## Files Created/Modified
- `___/middleware.py` - LoginRequiredMiddleware class with __call__ method checking request.user.is_authenticated, redirecting to LOGIN_URL with ?next= parameter
- `___/___/settings.py` - Added 'middleware.LoginRequiredMiddleware' to MIDDLEWARE list after AuthenticationMiddleware

## Decisions Made

**1. Custom middleware vs third-party package**
- **Decision:** Implement custom LoginRequiredMiddleware (~30 lines)
- **Rationale:** Zero external dependencies, simple logic, full control over exemptions
- **Alternative considered:** django-login-required-middleware package (rejected - adds dependency for minimal benefit)
- **Implementation:** Single class with __init__ and __call__ methods

**2. Middleware ordering**
- **Decision:** Place LoginRequiredMiddleware after AuthenticationMiddleware
- **Rationale:** LoginRequired needs request.user from AuthenticationMiddleware. If placed before, request.user won't exist yet and middleware will crash.
- **Source:** Research Pattern 4 from 02-RESEARCH.md
- **Final order:** Security → Session → Common → CSRF → Auth → Messages → Clickjacking → LoginRequired

**3. URL exemption strategy**
- **Decision:** Use startswith() for URL matching, not exact equality
- **Rationale:** Covers sub-paths automatically (e.g., '/admin/' matches '/admin/login/', '/admin/accounts/')
- **Implementation:** open_urls list with startswith() check in any() expression
- **Benefit:** Simpler exemption list, no need to enumerate every admin sub-path

**4. Exempt /static/ directory**
- **Decision:** Add '/static/' to open_urls exemptions
- **Rationale:** Login and register pages need CSS/JS files without authentication
- **Impact:** Prevents 302 redirect loops for static assets on authentication pages
- **Security note:** Static files are public by design, no sensitive data exposure

**5. ?next= parameter for post-login redirect**
- **Decision:** Include ?next= in redirect URL: f'{settings.LOGIN_URL}?next={path}'
- **Rationale:** Preserves user's intended destination, better UX after login
- **Implementation:** Redirect uses path variable from request.path_info
- **Integration:** Works with Django's LoginView which automatically handles ?next=

## Deviations from Plan

None - plan executed exactly as written. All tasks completed successfully with no blocking issues or scope changes.

## Issues Encountered

**Test client ALLOWED_HOSTS issue**
- **Problem:** Django test client uses 'testserver' as hostname, but ALLOWED_HOSTS in .env only had localhost and 127.0.0.1
- **Solution:** Used @override_settings decorator in test to temporarily add 'testserver' to ALLOWED_HOSTS
- **Impact:** No production code changes needed, test-only workaround
- **Learning:** Test client requires 'testserver' in ALLOWED_HOSTS when DEBUG=False

## Authentication Gates

None - no external authentication required during execution.

## Next Phase Readiness

**Phase 2 Complete:**
All authentication requirements satisfied:
- AUTH-01: Custom user model with cedula validation (02-01)
- AUTH-02: Registration form with data policy (02-02)
- AUTH-03: Login with remember me (02-02)
- AUTH-04: Cedula-based authentication (02-02)
- AUTH-05: Logout functionality (02-02)
- AUTH-06: Global login-required enforcement (02-03) ✓

**Ready for Phase 3:**
- Authentication foundation complete
- All routes now protected by default
- Login/register flow working end-to-end
- Session management configured
- ?next= parameter preserves intended destinations

**Blockers/Concerns:**
None - authentication system fully operational

**Notes for future phases:**
- Phase 3 should create /home/ landing page
- Update LOGIN_REDIRECT_URL from /admin/ to /home/
- All new routes automatically protected by LoginRequiredMiddleware
- Use @login_required decorator sparingly - global middleware handles most cases

**Key Pattern Established:**
Global middleware for cross-cutting concerns (authentication, logging, etc.) - cleaner than decorating every view

---
*Phase: 02-authentication-system*
*Completed: 2026-01-19*
