# Requirements: ___

**Defined:** 2026-01-18
**Core Value:** Users can securely register and authenticate to access the portal

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Authentication

- [ ] **AUTH-01**: User can register with username, password, Nombre Completo, Cédula, Phone, and data policy acceptance
- [ ] **AUTH-02**: Colombian cédula validated (6-10 digits format)
- [ ] **AUTH-03**: User can log in with username and password
- [ ] **AUTH-04**: "Remember me" option extends session duration
- [ ] **AUTH-05**: User can log out from home page
- [ ] **AUTH-06**: All unauthenticated requests redirect to login page

### Pages

- [ ] **PAGE-01**: Login page with username, password, remember me fields
- [ ] **PAGE-02**: Registration page with all required fields
- [ ] **PAGE-03**: Home page with logout button (post-login landing)

### Infrastructure

- [ ] **INFRA-01**: SQLite database (default Django)
- [ ] **INFRA-02**: Environment-based SECRET_KEY (.env file)
- [ ] **INFRA-03**: .gitignore for Python/Django project

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
| AUTH-01 | TBD | Pending |
| AUTH-02 | TBD | Pending |
| AUTH-03 | TBD | Pending |
| AUTH-04 | TBD | Pending |
| AUTH-05 | TBD | Pending |
| AUTH-06 | TBD | Pending |
| PAGE-01 | TBD | Pending |
| PAGE-02 | TBD | Pending |
| PAGE-03 | TBD | Pending |
| INFRA-01 | TBD | Pending |
| INFRA-02 | TBD | Pending |
| INFRA-03 | TBD | Pending |

**Coverage:**
- v1 requirements: 12 total
- Mapped to phases: 0
- Unmapped: 12 ⚠️

---
*Requirements defined: 2026-01-18*
*Last updated: 2026-01-18 after initial definition*
