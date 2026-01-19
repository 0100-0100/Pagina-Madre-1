# Roadmap: v1.2 Referrals

**Milestone:** v1.2 Referrals
**Created:** 2026-01-19
**Phases:** 4 (7-10)
**Depth:** Standard

## Overview

Add referral tracking system to the authentication portal. Users get unique referral codes, can share links to recruit others, track progress toward goals, manage their profile, and view their referral list. Four phases: model foundation with registration capture, home page referral UI, profile management, and referidos table.

---

## Phase 7: Referral Model & Registration

**Goal:** Users can register via referral links and the system tracks referrer relationships.

**Dependencies:** None (extends existing CustomUser model)

**Plans:** 2 plans

Plans:
- [ ] 07-01-PLAN.md — Add referral fields to CustomUser model with migrations
- [ ] 07-02-PLAN.md — Modify registration view to capture referral codes

**Requirements:**
- REF-01: CustomUser has unique 8-char alphanumeric referral_code field (auto-generated)
- REF-02: CustomUser has referred_by ForeignKey to self (on_delete=SET_NULL)
- REF-03: CustomUser has referral_goal PositiveIntegerField (default=10)
- REF-04: Existing users receive referral codes via data migration
- REG-01: Registration URL accepts `?ref=CODE` parameter
- REG-02: Valid referral code sets referred_by on new user
- REG-03: Invalid or missing referral code proceeds without error

**Success Criteria:**
1. Every user (new and existing) has a unique 8-character referral code visible in admin
2. Visiting `/register/?ref=VALIDCODE` and completing registration creates user with correct referred_by
3. Visiting `/register/?ref=INVALIDCODE` or `/register/` (no param) completes registration normally without errors
4. Deleting a referrer user preserves the referred user's account (SET_NULL behavior)

---

## Phase 8: Home Page Referral UI

**Goal:** Users can see their referral progress and share their unique link from the home page.

**Dependencies:** Phase 7 (referral_code, referred_by fields exist)

**Requirements:**
- HOME-01: Home page displays total referral count
- HOME-02: Home page displays progress toward goal ("X de Y referidos")
- HOME-03: Home page shows shareable referral link
- HOME-04: Home page has navigation links to Perfil and Referidos pages

**Success Criteria:**
1. Home page shows "X referidos" count matching actual referred users
2. Home page shows progress bar or text "X de Y referidos" reflecting user's goal
3. Home page displays full shareable URL (e.g., `http://localhost:8000/register/?ref=ABC12345`)
4. Home page has clickable navigation links to "/perfil/" and "/referidos/" pages

---

## Phase 9: Profile Page

**Goal:** Users can manage their account details and set their referral goal.

**Dependencies:** Phase 7 (referral_goal field exists), Phase 8 (navigation link exists)

**Requirements:**
- PROF-01: Profile page allows editing nombre_completo
- PROF-02: Profile page allows editing telefono
- PROF-03: Profile page allows changing password
- PROF-04: Profile page allows setting/updating referral goal

**Success Criteria:**
1. User can update nombre_completo and see change reflected after save
2. User can update telefono and see change reflected after save
3. User can change password, log out, and log in with new password
4. User can set referral goal (e.g., from 10 to 20) and see updated goal on home page

---

## Phase 10: Referidos Page

**Goal:** Users can view details of everyone they have referred.

**Dependencies:** Phase 7 (referred_by relationship), Phase 8 (navigation link exists)

**Requirements:**
- REFR-01: Referidos page displays table with columns: Nombre, Cedula, Telefono, Fecha de registro
- REFR-02: Empty state shows message when user has no referrals

**Success Criteria:**
1. User with referrals sees table listing each referred user's nombre, cedula, telefono, and registration date
2. User with zero referrals sees friendly empty state message (not empty table or error)

---

## Progress

| Phase | Name | Requirements | Status |
|-------|------|--------------|--------|
| 7 | Referral Model & Registration | 7 | Planned |
| 8 | Home Page Referral UI | 4 | Pending |
| 9 | Profile Page | 4 | Pending |
| 10 | Referidos Page | 2 | Pending |

**Total:** 17 requirements across 4 phases

---

## Coverage Validation

| Requirement | Phase | Mapped |
|-------------|-------|--------|
| REF-01 | 7 | Yes |
| REF-02 | 7 | Yes |
| REF-03 | 7 | Yes |
| REF-04 | 7 | Yes |
| REG-01 | 7 | Yes |
| REG-02 | 7 | Yes |
| REG-03 | 7 | Yes |
| HOME-01 | 8 | Yes |
| HOME-02 | 8 | Yes |
| HOME-03 | 8 | Yes |
| HOME-04 | 8 | Yes |
| PROF-01 | 9 | Yes |
| PROF-02 | 9 | Yes |
| PROF-03 | 9 | Yes |
| PROF-04 | 9 | Yes |
| REFR-01 | 10 | Yes |
| REFR-02 | 10 | Yes |

**Coverage:** 17/17 requirements mapped (100%)

---
*Roadmap created: 2026-01-19*
