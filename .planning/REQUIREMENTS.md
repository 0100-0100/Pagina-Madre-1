# Requirements: ___

**Defined:** 2026-01-18
**Core Value:** Users can securely register and authenticate to access the portal

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Authentication

- [x] **AUTH-01**: User can register with cedula, password, Nombre Completo, Phone, and data policy acceptance
- [x] **AUTH-02**: Colombian cédula validated (6-10 digits format)
- [x] **AUTH-03**: User can log in with cedula and password
- [x] **AUTH-04**: "Remember me" option extends session duration
- [x] **AUTH-05**: User can log out
- [x] **AUTH-06**: All unauthenticated requests redirect to login page

### Pages

- [x] **PAGE-01**: Login page with cedula, password, remember me fields
- [x] **PAGE-02**: Registration page with all required fields
- [x] **PAGE-03**: Home page with logout button (post-login landing)

### Infrastructure

- [x] **INFRA-01**: SQLite database (default Django)
- [x] **INFRA-02**: Environment-based SECRET_KEY (.env file)
- [x] **INFRA-03**: .gitignore for Python/Django project

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Deployment

- **DEPLOY-01**: PostgreSQL database configuration
- **DEPLOY-02**: AWS/cloud deployment configuration
- **DEPLOY-03**: HTTPS enforcement
- **DEPLOY-04**: Production SECRET_KEY management

### Enhanced Auth

- **EAUTH-01**: Password reset via email
- **EAUTH-02**: Email verification on registration
- **EAUTH-03**: OAuth/social login

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| OAuth/social login | Adds complexity, not needed for v1 |
| Email verification | Can add later if needed |
| Password reset via email | Can add later |
| 2FA/MFA | Defer to future version |
| User profile editing | v1 is just auth flow |
| Admin dashboard customization | Django admin is sufficient |
| Mobile app | Web only for now |

## Traceability

Which phases cover which requirements. Updated by create-roadmap.

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 | Phase 2 | Complete |
| AUTH-02 | Phase 2 | Complete |
| AUTH-03 | Phase 2 | Complete |
| AUTH-04 | Phase 2 | Complete |
| AUTH-05 | Phase 2 | Complete |
| AUTH-06 | Phase 2 | Complete |
| PAGE-01 | Phase 2 | Complete |
| PAGE-02 | Phase 2 | Complete |
| PAGE-03 | Phase 3 | Complete |
| INFRA-01 | Phase 1 | Complete |
| INFRA-02 | Phase 1 | Complete |
| INFRA-03 | Phase 1 | Complete |

**Coverage:**
- v1 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0

---
*Requirements defined: 2026-01-18*
*Last updated: 2026-01-19 after Phase 3 completion*
