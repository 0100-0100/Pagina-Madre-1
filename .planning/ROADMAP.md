# Roadmap: ___ (v1.1 UI Polish)

## Overview

Transform the functional but minimal authentication portal into a professional, responsive application using Bootstrap 5. Three phases: establish the Bootstrap foundation, style the authentication pages (login + register), then polish the home page with navigation.

## Milestones

- ✅ **v1.0 MVP** - Phases 1-3 (shipped 2026-01-19)
- 🚧 **v1.1 UI Polish** - Phases 4-6 (in progress)

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Foundation** - Project scaffolding (v1.0)
- [x] **Phase 2: Authentication System** - User model and auth views (v1.0)
- [x] **Phase 3: Protected Portal** - Home page and middleware (v1.0)
- [ ] **Phase 4: Bootstrap Foundation** - Base template with CDN includes
- [ ] **Phase 5: Styled Auth Pages** - Login and registration form styling
- [ ] **Phase 6: Styled Home Page** - Navbar and content layout

## Phase Details

<details>
<summary>✅ v1.0 MVP (Phases 1-3) - SHIPPED 2026-01-19</summary>

### Phase 1: Foundation
**Goal**: Project scaffolding and configuration
**Plans**: 1 plan (completed)

### Phase 2: Authentication System
**Goal**: User registration and login functionality
**Plans**: 3 plans (completed)

### Phase 3: Protected Portal
**Goal**: Protected home page with logout
**Plans**: 1 plan (completed)

</details>

### 🚧 v1.1 UI Polish (In Progress)

**Milestone Goal:** Professional, responsive styling with Bootstrap 5

#### Phase 4: Bootstrap Foundation
**Goal**: Base template with Bootstrap 5.3.8 CDN integration
**Depends on**: Phase 3 (existing templates to extend)
**Requirements**: R1, R2, R3
**Success Criteria** (what must be TRUE):
  1. Opening any page loads Bootstrap CSS without console errors
  2. All existing pages extend base.html and render correctly
  3. Pages display appropriately on mobile viewport (375px)
**Research flag**: Unlikely (standard Bootstrap CDN patterns)
**Plans**: 1 plan

Plans:
- [ ] 04-01-PLAN.md — Create base template with Bootstrap CDN and migrate existing templates to inheritance pattern

#### Phase 5: Styled Auth Pages
**Goal**: Professional login and registration forms with validation feedback
**Depends on**: Phase 4
**Requirements**: R4, R5, R6, R7, R8, R9, R10, R11, R12, R13, R17, R18
**Success Criteria** (what must be TRUE):
  1. Login form displays in centered card with styled fields and checkbox
  2. Registration form displays in centered card with all fields styled
  3. Form validation errors show with Bootstrap styling
  4. Django messages appear as Bootstrap alerts
  5. Forms work correctly on mobile devices
**Research flag**: Unlikely (form styling well-documented in research)
**Plans**: TBD

Plans:
- [ ] 05-01: Update forms.py with widget classes and style login template
- [ ] 05-02: Style registration template with form validation

#### Phase 6: Styled Home Page
**Goal**: Welcoming dashboard with navigation bar
**Depends on**: Phase 5
**Requirements**: R14, R15, R16
**Success Criteria** (what must be TRUE):
  1. Bootstrap navbar displays at page top with user's name
  2. Logout button is visible and styled in navbar
  3. Page content has proper spacing and margins
**Research flag**: Unlikely (standard Bootstrap navbar component)
**Plans**: TBD

Plans:
- [ ] 06-01: Add navbar and style home page content

## Progress

**Execution Order:**
Phases execute in numeric order: 4 → 5 → 6

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation | v1.0 | 1/1 | Complete | 2026-01-17 |
| 2. Authentication System | v1.0 | 3/3 | Complete | 2026-01-18 |
| 3. Protected Portal | v1.0 | 1/1 | Complete | 2026-01-19 |
| 4. Bootstrap Foundation | v1.1 | 0/1 | Not started | - |
| 5. Styled Auth Pages | v1.1 | 0/2 | Not started | - |
| 6. Styled Home Page | v1.1 | 0/1 | Not started | - |
