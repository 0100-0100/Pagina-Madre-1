# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-22)

**Core value:** Users can securely register and authenticate to access the portal.
**Current focus:** Planning next milestone (v1.4)

## Current Position

Phase: None active
Plan: N/A
Status: v1.3 Milestone SHIPPED - Ready for next milestone
Last activity: 2026-01-22 — v1.3 Async Background Jobs complete

Progress: Ready for v1.4 planning

## Milestones Shipped

- **v1.3 Async Background Jobs** (2026-01-22) - Phases 11-16, 9 plans, 32 requirements
- **v1.2 Referrals** (2026-01-19) - Phases 7-10, 5 plans
- **v1.1 UI Polish** (2026-01-19) - Phases 4-6, 4 plans
- **v1.0 MVP** (2026-01-19) - Phases 1-3, 5 plans

See: .planning/MILESTONES.md for full history

## Accumulated Context

### Key Decisions (carry forward)

- Cedula as username pattern established
- Session security with HTTPONLY, SAMESITE
- Custom middleware for global auth
- Bootstrap 5.3.8 via jsDelivr CDN with SRI
- Real-time validation with 1.5s debounce
- Input filtering for form fields
- Three-step migration for unique fields
- Self-referential ForeignKey with SET_NULL
- filter().first() for graceful referral lookup
- Django PasswordChangeView extension
- navigator.clipboard API for copy functionality
- ORM broker with SQLite for task queue (<100 users)
- Single worker (workers=1) for SQLite write safety
- WAL mode via connection_created signal
- timeout=120s, retry=180s for cedula validation tasks
- 9 granular status choices for CedulaInfo lifecycle
- TextField for raw_response (debug storage, not queried)
- Spanish verbose_names for all user-facing fields
- Role enum inside CustomUser class for namespacing (CustomUser.Role.USER)
- CedulaInfoAdmin fully read-only (data from scraping only)
- Role field read-only for non-superusers
- Browser singleton with lazy initialization for Playwright
- Fresh context per scrape with cleanup in finally block
- Headed browser mode when DEBUG=True for visual debugging
- CSS selectors as module constants for easy maintenance
- Class-level rate limiting (5s minimum between requests)
- 2captcha for reCAPTCHA solving (fully automated)
- Wait for networkidle before interacting with page
- Pattern-based response type detection (not_found, cancelled, found)
- dispatch_uid for signal deduplication
- schedule() with schedule_type='O' for one-time delayed retry
- Status PROCESSING during scrape (matches model choices)
- HTMX 2.0.4 with SRI from unpkg CDN for dynamic updates
- Conditional polling via data-polling attribute checked in hx-trigger
- 5-second polling interval for PENDING/PROCESSING states
- Census section as separate card below profile form
- leader_or_self_required decorator for RBAC checks (self-access first, then role)
- 30-second server-side cooldown using fetched_at timestamp
- HX-Trigger JSON header for showToast events
- Status set to PROCESSING before returning to avoid race conditions
- Checkbox visibility only for non-final statuses (excludes ACTIVE/CANCELLED from bulk refresh)
- Max 10 bulk refresh limit to prevent queue overload
- Client-side filtering and sorting for instant response on referidos table
- Empty response partial for HTMX toast-only responses
- Expandable table rows with detail sections for voting location display

### Pending Todos

- Future: Add semi-automated CAPTCHA fallback (leader manually solves in headed browser mode)
- Future: Don't refresh NOT_FOUND cedulas (they won't change)

### Blockers/Concerns

(None)

## Session Continuity

Last session: 2026-01-22
Stopped at: v1.3 Milestone SHIPPED
Resume file: None
Next: /gsd:new-milestone to plan v1.4

## To Resume Development

**v1.3 Milestone SHIPPED** (2026-01-22)

All 4 milestones complete:
- v1.0 MVP (Phases 1-3)
- v1.1 UI Polish (Phases 4-6)
- v1.2 Referrals (Phases 7-10)
- v1.3 Async Background Jobs (Phases 11-16)

**Next steps:**
- `/gsd:new-milestone` to define v1.4 goals and requirements
