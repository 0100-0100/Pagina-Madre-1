# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-19)

**Core value:** Users can securely register and authenticate to access the portal.
**Current focus:** v1.2 Referrals - Add referral tracking with shareable links and profile management

## Current Position

Phase: 7 - Referral Model & Registration
Plan: 01 complete
Status: Plan 07-01 complete, continue with phase planning
Last activity: 2026-01-19 - Completed 07-01-PLAN.md

Progress: [##--------] 25% (1/4 plans in phase 7)

## Current Milestone: v1.2 Referrals

**Goal:** Add referral system with tracking, profile management, and referral details page

**Phases:**
| Phase | Name | Requirements | Status |
|-------|------|--------------|--------|
| 7 | Referral Model & Registration | 7 | In Progress (1 plan done) |
| 8 | Home Page Referral UI | 4 | Pending |
| 9 | Profile Page | 4 | Pending |
| 10 | Referidos Page | 2 | Pending |

**Next:** Continue Phase 7 planning or execute remaining plans

## Milestones Shipped

- **v1.0 MVP** (2026-01-19) - Phases 1-3, 5 plans
- **v1.1 UI Polish** (2026-01-19) - Phases 4-6, 4 plans

See: .planning/MILESTONES.md for full history

## Accumulated Context

### Key Decisions (carry forward)

- Cedula as username pattern established
- Session security with HTTPONLY, SAMESITE
- Custom middleware for global auth
- Bootstrap 5.3.8 via jsDelivr CDN with SRI
- Real-time validation with 1.5s debounce
- Input filtering for form fields
- SeparateDatabaseAndState for SQLite unique constraint migrations
- Three-step migration for unique fields: add nullable, populate, add constraint

### v1.2 Technical Notes

- Use `django.utils.crypto.get_random_string` for referral code generation
- Self-referential ForeignKey with `on_delete=SET_NULL` preserves history
- Django's built-in PasswordChangeView for password changes
- Bootstrap progress bar for goal display
- Navbar extraction to `includes/navbar.html` for DRY
- Callable default pattern: `default=generate_referral_code` (no parentheses)

### Pending Todos

(None)

### Blockers/Concerns

(None)

## Session Continuity

Last session: 2026-01-19
Stopped at: Completed 07-01-PLAN.md
Resume file: .planning/phases/07-referral-model-registration/07-01-SUMMARY.md
Next: Continue with next plan in Phase 7 or plan remaining requirements

## To Resume Development

Phase 7 Plan 01 complete. CustomUser model now has referral fields. Continue with next plan for registration form integration with referred_by.
