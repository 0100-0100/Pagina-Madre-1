# Research Summary: v1.1 UI Polish

**Project:** ___ (Django Authentication Portal)
**Milestone:** v1.1 UI Polish
**Research Date:** 2026-01-19
**Confidence:** HIGH

## Executive Summary

Bootstrap 5.3.8 integration via CDN is the optimal approach for this project. No Django packages needed — the 3-template scope doesn't justify package overhead. Create a base template with Bootstrap includes, extend existing templates, and apply Bootstrap classes to forms and layouts.

**Key insight:** The primary challenge is Django form widget styling, not Bootstrap itself. Forms render without Bootstrap classes by default — this requires explicit widget class assignment in forms.py.

## Stack Decision

**Use Bootstrap 5.3.8 via jsDelivr CDN:**

```html
<!-- CSS in <head> -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css"
      rel="stylesheet"
      integrity="sha384-..."
      crossorigin="anonymous">

<!-- JS before </body> -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-..."
        crossorigin="anonymous"></script>
```

**No pip packages. No settings.py changes. No build process.**

**Rejected alternatives:**
- django-bootstrap5 — Excellent but overkill for 3 templates
- django-crispy-forms — Unnecessary complexity for simple auth forms
- npm + static files — Adds build complexity without benefit

## Feature Requirements

**Table Stakes (must have):**
1. Card-based form containers with shadow
2. Form controls with `form-control` class
3. Form validation feedback (`.is-invalid`, `.invalid-feedback`)
4. Alert component for Django messages
5. Primary button styling
6. Checkbox components (`.form-check`)
7. Responsive mobile-first layout
8. Proper spacing utilities

**Nice-to-haves (if time permits):**
- Input group icons (Bootstrap Icons)
- Password visibility toggle
- Loading state on submit buttons

**Anti-features (avoid):**
- Social login buttons without backend
- Floating labels (accessibility concerns)
- Modal/popup login forms
- Custom checkbox styling beyond Bootstrap

## Architecture Pattern

**Template inheritance hierarchy:**

```
templates/
├── base.html              # Bootstrap CDN includes, common blocks
├── home.html              # Extends base.html
└── registration/
    ├── login.html         # Extends base.html
    └── register.html      # Extends base.html
```

**Base template blocks:**
- `title` — Page title
- `extra_css` — Page-specific styles
- `content` — Main page content (each page controls its own grid)
- `extra_js` — Page-specific scripts

**Key principle:** Bootstrap grid (container/row/col) lives in child templates, not base. Each page controls its own layout.

## Critical Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Forms render without Bootstrap classes | Override widget attrs in forms.py `__init__` |
| Checkboxes need specific wrapper structure | Manual HTML with `.form-check` div wrapper |
| CSRF token placement | Put `{% csrf_token %}` first inside `<form>` |
| Inherited password fields lack styling | Override in CustomUserCreationForm `__init__` |
| Missing viewport meta tag | Add `<meta name="viewport" ...>` in base.html |

**Your specific forms need:**
- `CustomUserCreationForm`: Override `__init__` to add `form-control` to password1/password2
- `data_policy_accepted`: Manual checkbox HTML with `.form-check` wrapper
- `remember_me`: Same manual checkbox treatment
- All text inputs: Add `form-control` class via widget attrs

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 4: Bootstrap Foundation

**Goal:** Base template with Bootstrap CDN and responsive structure

**Tasks:**
1. Create `base.html` with Bootstrap 5.3.8 CDN includes
2. Add viewport meta tag for mobile responsiveness
3. Define template blocks (title, content, extra_css, extra_js)
4. Update existing templates to extend base.html

**Addresses:** FEATURES (responsive layout), ARCHITECTURE (template inheritance)
**Avoids:** PITFALLS (missing viewport, duplicate includes)

### Phase 5: Styled Auth Pages

**Goal:** Professional login and registration forms

**Tasks:**
1. Update `CustomUserCreationForm` widget classes in forms.py
2. Style login.html with Bootstrap card, form controls, checkbox
3. Style register.html with Bootstrap card, form controls, checkboxes
4. Add form validation feedback classes
5. Style alert messages for Django messages framework

**Addresses:** FEATURES (card, forms, validation, alerts), STACK (form-control classes)
**Avoids:** PITFALLS (unstyled widgets, broken checkboxes, missing validation styling)

### Phase 6: Styled Home Page

**Goal:** Welcoming dashboard with navigation

**Tasks:**
1. Add Bootstrap navbar component
2. Style user greeting and logout button
3. Ensure responsive layout

**Addresses:** FEATURES (dashboard, navbar)
**Uses:** STACK (Bootstrap components)

**Phase ordering rationale:**
- Foundation first → all other templates inherit Bootstrap includes
- Auth pages before home → users see styled pages at first interaction
- Forms.py changes in Phase 5 → affects both login and register

**Research flags for phases:**
- Phase 4: Standard patterns, unlikely to need additional research
- Phase 5: Form widget styling is well-documented but requires attention
- Phase 6: Standard Bootstrap components, straightforward

## Estimated Effort

| Phase | Estimate |
|-------|----------|
| Phase 4: Foundation | 1-2 hours |
| Phase 5: Auth Pages | 3-4 hours |
| Phase 6: Home Page | 1-2 hours |
| **Total** | **5-8 hours** |

## Open Questions

None — Bootstrap 5 + Django integration is well-documented with stable patterns.

## Sources

- Bootstrap 5.3 Official Documentation (getbootstrap.com)
- Django Template Language Documentation (djangoproject.com)
- LearnDjango Best Practices
- django-bootstrap5 Documentation
- Multiple community tutorials and Stack Overflow answers

---

*Research complete. Ready for `/gsd:define-requirements` or `/gsd:create-roadmap`.*
