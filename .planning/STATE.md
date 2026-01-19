# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-19)

**Core value:** Users can securely register and authenticate to access the portal.
**Current focus:** v1.2 Referrals - Add referral tracking with shareable links and profile management

## Current Position

Phase: 9 - Profile Page
Plan: 01 of 01 complete
Status: Phase 9 complete
Last activity: 2026-01-19 - Completed 09-01-PLAN.md

Progress: [########--] 75% (3/4 phases complete in v1.2)

## Current Milestone: v1.2 Referrals

**Goal:** Add referral system with tracking, profile management, and referral details page

**Phases:**
| Phase | Name | Requirements | Status |
|-------|------|--------------|--------|
| 7 | Referral Model & Registration | 7 | Complete |
| 8 | Home Page Referral UI | 4 | Complete |
| 9 | Profile Page | 4 | Complete |
| 10 | Referidos Page | 2 | Pending |

**Next:** Plan Phase 10 with `/gsd:plan-phase 10`

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
- Use filter().first() for graceful referral lookup (no exception on missing)
- ProfileForm excludes cedula (read-only display only)
- Password change redirects to profile page with success toast

### v1.2 Technical Notes

- Use `django.utils.crypto.get_random_string` for referral code generation
- Self-referential ForeignKey with `on_delete=SET_NULL` preserves history
- Django's built-in PasswordChangeView for password changes
- Bootstrap progress bar for goal display
- Navbar extraction to `includes/navbar.html` for DRY
- Callable default pattern: `default=generate_referral_code` (no parentheses)
- Registration captures ?ref=CODE and sets referred_by on new users
- Use navigator.clipboard API for clipboard copy with fallback alert
- Bootstrap Icons 1.13.1 via jsDelivr CDN for navigation icons
- Placeholder routes (return "Coming soon") prevent NoReverseMatch errors
- Form instance binding: ProfileForm(instance=request.user)
- PasswordChangeView extension with success message

### Pending Todos

(None)

### Blockers/Concerns

(None)

## Session Continuity

Last session: 2026-01-19
Stopped at: Phase 9 complete
Resume file: .planning/phases/09-profile-page/09-01-SUMMARY.md
Next: `/gsd:plan-phase 10` to plan Referidos Page

## To Resume Development

Phase 9 complete. Profile page at /perfil/ allows editing nombre, phone, and referral_goal. Password change at /cambiar-password/ with Django's secure handling. Ready to proceed to Phase 10 (Referidos Page).
