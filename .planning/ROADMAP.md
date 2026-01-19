# Roadmap

**Project:** ___ (Django Authentication Portal)
**Created:** 2026-01-18
**Phases:** 3

## Overview

This roadmap delivers a secure Django authentication portal in three focused phases. Phase 1 establishes infrastructure foundations, Phase 2 implements the complete authentication system with custom user model and Colombian cédula validation, and Phase 3 delivers the protected portal experience with login-required enforcement.

## Phases

### Phase 1: Foundation

**Goal:** Project infrastructure is configured and ready for development
**Depends on:** Nothing (first phase)
**Requirements:** INFRA-01, INFRA-02, INFRA-03

**Success Criteria:**
1. Developer can run Django development server without errors
2. SECRET_KEY is loaded from .env file (not hardcoded)
3. Git repository excludes sensitive files (.env, db.sqlite3, __pycache__, .venv)
4. SQLite database is configured and migrations run successfully

**Plans:** 1 plan

Plans:
- [x] 01-01-PLAN.md — Configure infrastructure (requirements, .gitignore, .env, settings)

---

### Phase 2: Authentication System

**Goal:** Users can register with Colombian cédula and log in to access the portal
**Depends on:** Phase 1
**Requirements:** AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05, AUTH-06, PAGE-01, PAGE-02

**Success Criteria:**
1. User can register with username, password, Nombre Completo, Cédula (6-10 digits validated), Phone, and data policy acceptance
2. User can log in with username and password immediately after registration
3. User can check "Remember me" to extend session duration beyond browser close
4. All unauthenticated requests redirect to login page
5. Registration page displays all required fields with proper validation
6. Login page displays username, password, and "Remember me" fields

**Plans:** 3 plans

Plans:
- [x] 02-01-PLAN.md — Custom User model with cedula validation and admin integration
- [x] 02-02-PLAN.md — Registration and login views with remember me functionality
- [x] 02-03-PLAN.md — Global login-required middleware

---

### Phase 3: Protected Portal

**Goal:** Authenticated users access home page and can log out
**Depends on:** Phase 2
**Requirements:** PAGE-03

**Success Criteria:**
1. User sees home page immediately after successful login
2. Home page displays user's name or username
3. User can click logout button from home page and return to login
4. Unauthenticated access to home page redirects to login

**Plans:** 1 plan

Plans:
- [ ] 03-01-PLAN.md — Home page with user info and logout functionality

---

## Progress

| Phase | Status | Completed |
|-------|--------|-----------|
| 1 - Foundation | ✓ Complete | 2026-01-18 |
| 2 - Authentication System | ✓ Complete | 2026-01-19 |
| 3 - Protected Portal | Not started | — |

---

*Roadmap for milestone: v1.0*
