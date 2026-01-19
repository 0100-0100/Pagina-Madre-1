# Requirements: v1.1 UI Polish

**Project:** ___ (Django Authentication Portal)
**Milestone:** v1.1 UI Polish
**Created:** 2026-01-19
**Status:** Active

## Goal

Apply Bootstrap 5 styling to all pages for a professional, responsive look without adding package dependencies.

---

## Must-Haves (8)

### Bootstrap Foundation
- [ ] **R1:** Base template (`base.html`) exists with Bootstrap 5.3.8 CDN includes and SRI integrity hashes
- [ ] **R2:** All pages extend base template and render without broken styles
- [ ] **R3:** Viewport meta tag present for mobile responsiveness

### Login Page Styling
- [ ] **R4:** Login form displays in centered Bootstrap card with shadow
- [ ] **R5:** Form fields have `form-control` class and proper labels
- [ ] **R6:** "Remember me" checkbox uses Bootstrap `.form-check` structure
- [ ] **R7:** Submit button is full-width primary Bootstrap button
- [ ] **R8:** Form validation feedback shows with Bootstrap `.is-invalid` and `.invalid-feedback` classes

### Registration Page Styling
- [ ] **R9:** Registration form displays in centered Bootstrap card with shadow
- [ ] **R10:** All form fields (cedula, nombre_completo, telefono, passwords) have `form-control` class
- [ ] **R11:** Data policy checkbox uses Bootstrap `.form-check` structure with required validation
- [ ] **R12:** Submit button is full-width primary Bootstrap button
- [ ] **R13:** Form validation feedback shows for all fields

### Home Page Styling
- [ ] **R14:** Bootstrap navbar displays at top with user identification
- [ ] **R15:** Logout button styled as Bootstrap button in navbar
- [ ] **R16:** Page content uses Bootstrap container for proper margins

### Django Integration
- [ ] **R17:** Django messages display as Bootstrap alerts (success/error variants)
- [ ] **R18:** Form widget classes applied in forms.py `__init__` method (not just templates)

---

## Nice-to-Haves (0 for v1.1)

*Deferred to future milestone to keep v1.1 scope focused:*
- Input group icons (requires Bootstrap Icons library)
- Password visibility toggle (requires JavaScript)
- Loading spinner on submit buttons (requires JavaScript)
- Gradient/glassmorphism card styling

---

## Out of Scope

*Explicitly excluded per research anti-features:*
- Social login buttons (no backend support)
- Password strength meter (Django handles validation)
- Multi-step registration wizard
- Custom checkbox/input styling beyond Bootstrap
- Modal/popup login forms
- Floating labels (accessibility concerns)

---

## Verification Criteria

**Foundation verified when:**
- Opening any page shows Bootstrap-styled elements
- No console errors related to missing Bootstrap resources
- Pages display correctly on mobile viewport (375px width)

**Auth pages verified when:**
- Forms are visually centered in card containers
- Invalid form submission shows styled error messages
- Checkbox controls render with Bootstrap styling

**Home page verified when:**
- Navbar displays user's name
- Logout button is visible and styled
- Content has proper margins/padding

---

## Technical Notes

**From research:**
- Use Bootstrap 5.3.8 via jsDelivr CDN (no npm/packages)
- Override widget attrs in `CustomUserCreationForm.__init__` for password fields
- Checkbox fields need manual HTML with `.form-check` wrapper
- CSRF token must be first inside `<form>` tag
- Grid layout belongs in child templates, not base template

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| R1 | Phase 4 | Complete |
| R2 | Phase 4 | Complete |
| R3 | Phase 4 | Complete |
| R4 | Phase 5 | Pending |
| R5 | Phase 5 | Pending |
| R6 | Phase 5 | Pending |
| R7 | Phase 5 | Pending |
| R8 | Phase 5 | Pending |
| R9 | Phase 5 | Pending |
| R10 | Phase 5 | Pending |
| R11 | Phase 5 | Pending |
| R12 | Phase 5 | Pending |
| R13 | Phase 5 | Pending |
| R14 | Phase 6 | Pending |
| R15 | Phase 6 | Pending |
| R16 | Phase 6 | Pending |
| R17 | Phase 5 | Pending |
| R18 | Phase 5 | Pending |

**Coverage:**
- v1.1 requirements: 18 total
- Mapped to phases: 18
- Unmapped: 0 ✓
