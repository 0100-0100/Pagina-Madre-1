# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-19)

**Core value:** Users can securely register and authenticate to access the portal.
**Current focus:** v1.2 Referrals - Add referral tracking with shareable links and profile management

## Current Position

Phase: 7 - Referral Model & Registration ✓
Plan: All plans complete
Status: Phase 7 complete, goal verified
Last activity: 2026-01-19 - Phase 7 execution complete

Progress: [##--------] 25% (1/4 phases complete in v1.2)

## Current Milestone: v1.2 Referrals

**Goal:** Add referral system with tracking, profile management, and referral details page

**Phases:**
| Phase | Name | Requirements | Status |
|-------|------|--------------|--------|
| 7 | Referral Model & Registration | 7 | ✓ Complete |
| 8 | Home Page Referral UI | 4 | Pending |
| 9 | Profile Page | 4 | Pending |
| 10 | Referidos Page | 2 | Pending |

**Next:** Plan Phase 8 with `/gsd:plan-phase 8`

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

### v1.2 Technical Notes

- Use `django.utils.crypto.get_random_string` for referral code generation
- Self-referential ForeignKey with `on_delete=SET_NULL` preserves history
- Django's built-in PasswordChangeView for password changes
- Bootstrap progress bar for goal display
- Navbar extraction to `includes/navbar.html` for DRY
- Callable default pattern: `default=generate_referral_code` (no parentheses)
- Registration captures ?ref=CODE and sets referred_by on new users

### Pending Todos

(None)

### Blockers/Concerns

(None)

## Session Continuity

Last session: 2026-01-19
Stopped at: Phase 7 complete and verified
Resume file: .planning/phases/07-referral-model-registration/07-VERIFICATION.md
Next: `/gsd:plan-phase 8` to plan Home Page Referral UI

## To Resume Development

Phase 7 complete. Users can now register via referral links (?ref=CODE) and the system tracks referrer relationships. All 7 requirements verified. Ready to proceed to Phase 8.
