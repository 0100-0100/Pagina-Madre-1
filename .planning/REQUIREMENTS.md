# Requirements: v1.2 Referrals

**Project:** ___ (Django Authentication Portal)
**Milestone:** v1.2 Referrals
**Created:** 2026-01-19
**Status:** Active

## Goal

Add referral tracking system with shareable links, profile management, and referral details page.

---

## Must-Haves (15)

### Referral Model
- [x] **REF-01:** CustomUser has unique 8-char alphanumeric referral_code field (auto-generated)
- [x] **REF-02:** CustomUser has referred_by ForeignKey to self (on_delete=SET_NULL)
- [x] **REF-03:** CustomUser has referral_goal PositiveIntegerField (default=10)
- [x] **REF-04:** Existing users receive referral codes via data migration

### Registration Flow
- [x] **REG-01:** Registration URL accepts `?ref=CODE` parameter
- [x] **REG-02:** Valid referral code sets referred_by on new user
- [x] **REG-03:** Invalid or missing referral code proceeds without error

### Home Page
- [ ] **HOME-01:** Home page displays total referral count
- [ ] **HOME-02:** Home page displays progress toward goal ("X de Y referidos")
- [ ] **HOME-03:** Home page shows shareable referral link
- [ ] **HOME-04:** Home page has navigation links to Perfil and Referidos pages

### Profile Page
- [ ] **PROF-01:** Profile page allows editing nombre_completo
- [ ] **PROF-02:** Profile page allows editing teléfono
- [ ] **PROF-03:** Profile page allows changing password
- [ ] **PROF-04:** Profile page allows setting/updating referral goal

### Referidos Page
- [ ] **REFR-01:** Referidos page displays table with columns: Nombre, Cédula, Teléfono, Fecha de registro
- [ ] **REFR-02:** Empty state shows message when user has no referrals

---

## Nice-to-Haves (3)

### UX Enhancements
- **UX-01:** Copy-to-clipboard button for referral link with visual feedback
- **UX-02:** Table zebra striping (`.table-striped`) for readability
- **UX-03:** Progress bar animation on home page

---

## Out of Scope

| Feature | Reason |
|---------|--------|
| Multi-level referral tracking | Adds MLM complexity, not requested |
| Referral rewards/incentives | Tracking only, per PROJECT.md |
| Self-referral prevention | Overkill for <100 users, manual review sufficient |
| Referral analytics dashboard | Overengineering for simple tracking |
| Editable cédula on profile | Cédula is identity/username, should not change |
| Table sorting/filtering | Unnecessary for small dataset |
| Referral link expiration | Not requested, links valid indefinitely |

---

## Technical Notes

**From research:**
- Use `django.utils.crypto.get_random_string` for code generation
- Self-referential ForeignKey with `on_delete=SET_NULL` preserves history
- Django's built-in PasswordChangeView for password changes
- Bootstrap progress bar for goal display
- Navbar extraction to `includes/navbar.html` for DRY

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| REF-01 | Phase 7 | Complete |
| REF-02 | Phase 7 | Complete |
| REF-03 | Phase 7 | Complete |
| REF-04 | Phase 7 | Complete |
| REG-01 | Phase 7 | Complete |
| REG-02 | Phase 7 | Complete |
| REG-03 | Phase 7 | Complete |
| HOME-01 | Phase 8 | Pending |
| HOME-02 | Phase 8 | Pending |
| HOME-03 | Phase 8 | Pending |
| HOME-04 | Phase 8 | Pending |
| PROF-01 | Phase 9 | Pending |
| PROF-02 | Phase 9 | Pending |
| PROF-03 | Phase 9 | Pending |
| PROF-04 | Phase 9 | Pending |
| REFR-01 | Phase 10 | Pending |
| REFR-02 | Phase 10 | Pending |

**Coverage:**
- v1.2 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0 ✓

---
*Requirements defined: 2026-01-19*
