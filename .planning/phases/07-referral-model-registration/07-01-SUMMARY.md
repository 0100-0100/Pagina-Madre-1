---
phase: 07-referral-model-registration
plan: 01
subsystem: database
tags: [django, models, migrations, referrals]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: CustomUser model with AbstractUser
provides:
  - CustomUser.referral_code (8-char unique, auto-generated)
  - CustomUser.referred_by (self-referential ForeignKey)
  - CustomUser.referral_goal (PositiveIntegerField, default=10)
  - Three-step migration pattern for unique fields on existing data
affects: [08-home-page-referral-ui, 09-profile-page, 10-referidos-page]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - SeparateDatabaseAndState for SQLite unique constraint migrations
    - Callable default for unique field generation

key-files:
  created:
    - ___/accounts/migrations/0002_add_referral_fields.py
    - ___/accounts/migrations/0003_populate_referral_codes.py
    - ___/accounts/migrations/0004_referral_unique_constraint.py
  modified:
    - ___/accounts/models.py
    - ___/accounts/admin.py

key-decisions:
  - "Use SeparateDatabaseAndState for SQLite unique constraint to avoid table recreation"
  - "Three-step migration: add nullable field, populate data, add unique constraint"

patterns-established:
  - "Callable default pattern: default=generate_referral_code (no parentheses)"
  - "Self-referential ForeignKey with SET_NULL preserves referral history"

# Metrics
duration: 12min
completed: 2026-01-19
---

# Phase 7 Plan 01: Referral Model Summary

**CustomUser extended with referral_code (8-char unique), referred_by (self-ref FK), and referral_goal (default=10)**

## Performance

- **Duration:** 12 min
- **Started:** 2026-01-19T20:00:00Z
- **Completed:** 2026-01-19T20:12:00Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Added three referral fields to CustomUser model
- Created three-step migration for adding unique field to existing data
- Updated admin with Referral Info section and read-only referral_code
- All existing users have unique 8-character alphanumeric codes

## Task Commits

Each task was committed atomically:

1. **Task 1: Add referral fields to CustomUser model** - `0bfeb7a` (feat)
2. **Task 2: Create and apply three-step migrations** - `b743c78` (feat)
3. **Task 3: Update admin to display referral fields** - `2c982b7` (feat)

## Files Created/Modified

- `___/accounts/models.py` - Added referral_code, referred_by, referral_goal fields
- `___/accounts/admin.py` - Added Referral Info section, readonly referral_code
- `___/accounts/migrations/0002_add_referral_fields.py` - Schema migration for new fields
- `___/accounts/migrations/0003_populate_referral_codes.py` - Data migration for existing users
- `___/accounts/migrations/0004_referral_unique_constraint.py` - Unique constraint via RunSQL

## Decisions Made

1. **SeparateDatabaseAndState for SQLite** - SQLite table recreation with unique constraints causes the default function to re-run for all rows. Used SeparateDatabaseAndState with RunSQL to add unique index directly, avoiding this issue.

2. **Three-step migration pattern** - Adding unique field to existing data requires: (1) add nullable field, (2) populate unique values, (3) add unique constraint. This ensures no constraint violations during migration.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] SQLite unique constraint migration failure**
- **Found during:** Task 2 (migrations)
- **Issue:** Django's AlterField recreates table on SQLite, causing default function to run for all rows and create duplicates
- **Fix:** Used SeparateDatabaseAndState with RunSQL to add unique index directly, regenerated codes for existing users
- **Files modified:** `___/accounts/migrations/0004_referral_unique_constraint.py`
- **Verification:** All migrations applied, unique constraint verified
- **Committed in:** b743c78 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** SQLite-specific workaround required. No scope creep.

## Issues Encountered

- SQLite does not support ALTER TABLE for most operations and remakes the table, which causes callable defaults to re-run. Solved with SeparateDatabaseAndState migration pattern.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Referral model foundation complete
- Ready for Phase 8: Home Page Referral UI
- referred_by field ready for registration form integration
- referral_code ready for shareable link generation

---
*Phase: 07-referral-model-registration*
*Completed: 2026-01-19*
