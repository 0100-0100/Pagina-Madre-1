# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-19)

**Core value:** Users can securely register and authenticate to access the portal.
**Current focus:** v1.2 Referrals - Add referral tracking with shareable links and profile management

## Current Position

Phase: 7 - Referral Model & Registration
Plan: Not started
Status: Roadmap created, ready for phase planning
Last activity: 2026-01-19 - Roadmap created for v1.2

Progress: [----------] 0% (0/4 phases complete)

## Current Milestone: v1.2 Referrals

**Goal:** Add referral system with tracking, profile management, and referral details page

**Phases:**
| Phase | Name | Requirements | Status |
|-------|------|--------------|--------|
| 7 | Referral Model & Registration | 7 | Pending |
| 8 | Home Page Referral UI | 4 | Pending |
| 9 | Profile Page | 4 | Pending |
| 10 | Referidos Page | 2 | Pending |

**Next:** Plan Phase 7 with `/gsd:plan-phase 7`

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

### v1.2 Technical Notes

- Use `django.utils.crypto.get_random_string` for referral code generation
- Self-referential ForeignKey with `on_delete=SET_NULL` preserves history
- Django's built-in PasswordChangeView for password changes
- Bootstrap progress bar for goal display
- Navbar extraction to `includes/navbar.html` for DRY

### Pending Todos

(None)

### Blockers/Concerns

(None)

## Session Continuity

Last session: 2026-01-19
Stopped at: Roadmap created for v1.2
Resume file: .planning/ROADMAP.md
Next: `/gsd:plan-phase 7` to plan Referral Model & Registration

## To Resume Development

Run `/gsd:plan-phase 7` to create the execution plan for Phase 7.
