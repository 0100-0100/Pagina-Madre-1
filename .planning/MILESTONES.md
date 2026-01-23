# Project Milestones: ___

## v1.3 Async Background Jobs (Shipped: 2026-01-22)

**Delivered:** Background task queue with automated cédula validation against Registraduría electoral census, featuring auto-trigger on registration, HTMX-powered status display, and leader bulk refresh capabilities.

**Phases completed:** 11-16 (9 plans total)

**Key accomplishments:**

- Django-Q2 background task queue with SQLite ORM broker and WAL mode for concurrent access
- CedulaInfo model with 9 status choices tracking full validation lifecycle
- Playwright headless browser scraper with 2captcha reCAPTCHA integration
- Auto-validation on registration via post_save signal with exponential backoff retry
- HTMX-powered census display with conditional polling (stops on final states)
- Leader RBAC: view referral census data, manual refresh, bulk refresh (max 10)
- 9 bugs found and fixed during manual testing phase

**Stats:**

- ~1,962 lines Python + ~2,337 lines HTML
- 6 phases, 9 plans, 32 requirements
- 4 days from start to ship (2026-01-19 → 2026-01-22)

**Git range:** `v1.2` → `v1.3`

**What's next:** Define v1.4 milestone with `/gsd:new-milestone`

---

## v1.2 Referrals (Shipped: 2026-01-19)

**Delivered:** Referral tracking system with shareable links, profile management, and referral details page.

**Phases completed:** 7-10 (5 plans total)

**Key accomplishments:**

- Referral tracking system with unique 8-char codes and self-referential relationships
- Registration captures `?ref=CODE` parameter to link new users to referrers
- Home page referral dashboard with progress bar and copy-to-clipboard link sharing
- Profile management page for editing nombre, phone, and referral goal
- Password change with Django's secure PasswordChangeView
- Referidos page with table of referred users and empty state

**Stats:**

- 35 files created/modified
- 1,828 lines of code (Python + HTML)
- 4 phases, 5 plans
- 3 days to ship

**Git range:** `0bfeb7a` → `b80020d`

**What's next:** Define v1.3 milestone with `/gsd:new-milestone`

---

## v1.1 UI Polish (Shipped: 2026-01-19)

**Delivered:** Professional Bootstrap 5 styling for all pages with responsive layouts, real-time form validation, and mobile-friendly design.

**Phases completed:** 4-6 (4 plans total)

**Key accomplishments:**

- Bootstrap 5.3.8 integration via jsDelivr CDN with SRI integrity hashes
- Base template with template inheritance pattern for all pages
- Professional login page with Bootstrap card, real-time validation, numeric-only cédula input
- Professional registration page with input filtering (cédula/phone: numeric, nombre: letters/accents)
- Responsive home page with navbar showing user name and styled logout button
- Mobile-responsive design across all pages

**Stats:**

- 23 files created/modified
- 1,318 lines of code (534 Python + 784 HTML)
- 3 phases, 4 plans
- 1 day to ship

**Git range:** `a461b3f` → `4240d2e`

**What's next:** Define v1.2 milestone with `/gsd:new-milestone`

---

## v1.0 MVP (Shipped: 2026-01-19)

**Delivered:** Complete authentication portal with Colombian cédula-based login, registration, and protected routes.

**Phases completed:** 1-3 (5 plans total)

**Key accomplishments:**

- Custom User model with Colombian cédula validation (6-10 digits)
- Cédula-as-username pattern for simplified authentication
- Remember me session control (browser close vs 14 days)
- Global login-required middleware protecting all routes
- Complete auth flow: register → auto-login → home → logout

**Stats:**

- 17 Python files created/modified
- 459 lines of Python + 93 lines of HTML
- 3 phases, 5 plans
- 3 days from start to ship

**Git range:** `bb3117d` → `260e198`

**What's next:** TBD — run `/gsd:discuss-milestone` to plan next version

---
