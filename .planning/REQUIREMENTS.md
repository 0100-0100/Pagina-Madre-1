# Requirements: v1.3 Async Background Jobs

**Defined:** 2026-01-19
**Core Value:** Users can securely register and authenticate to access the portal.

## v1.3 Requirements

Requirements for v1.3 milestone. Each maps to roadmap phases.

### Infrastructure

- [ ] **INFRA-01**: Django-Q2 task queue installed and configured with ORM broker
- [ ] **INFRA-02**: SQLite WAL mode enabled to prevent database locking
- [ ] **INFRA-03**: Task worker process (qcluster) runs successfully
- [ ] **INFRA-04**: Task timeout and retry configured (timeout=120s, retry=180s)

### Scraping

- [ ] **SCRP-01**: Playwright headless browser installed with Chromium
- [ ] **SCRP-02**: Stealth patches applied to avoid bot detection
- [ ] **SCRP-03**: Scraper handles "active" response (voting location data)
- [ ] **SCRP-04**: Scraper handles "cancelled" response (deceased/novedad data)
- [ ] **SCRP-05**: Scraper handles "not found" response
- [ ] **SCRP-06**: Scraper handles errors gracefully (timeout, network, bot block)
- [ ] **SCRP-07**: Rate limiting between requests (minimum 5 seconds)

### Data Model

- [ ] **DATA-01**: CedulaInfo model created with OneToOne link to CustomUser
- [ ] **DATA-02**: Status field with choices: PENDING, FOUND, NOT_FOUND, CANCELLED, ERROR
- [ ] **DATA-03**: Voting location fields: departamento, municipio, puesto, direccion, mesa
- [ ] **DATA-04**: Cancelled fields: novedad, resolucion, fecha_novedad
- [ ] **DATA-05**: Metadata fields: fetched_at, error_message, raw_response
- [ ] **DATA-06**: CedulaInfo registered in Django admin (read-only display)

### Triggers

- [ ] **TRIG-01**: Background task auto-triggers on user registration via post_save signal
- [ ] **TRIG-02**: Signal uses transaction.on_commit() to avoid race conditions
- [ ] **TRIG-03**: Retry logic with exponential backoff (max 3 attempts)

### RBAC (Role-Based Access Control)

- [ ] **RBAC-01**: Role field added to CustomUser with choices: USER, LEADER
- [ ] **RBAC-02**: Default role is USER for new registrations
- [ ] **RBAC-03**: Only Django superadmin can change user roles (via admin)
- [ ] **RBAC-04**: Leader can view census data for users they referred
- [ ] **RBAC-05**: Leader sees manual refresh button for individual referred users
- [ ] **RBAC-06**: Leader has bulk refresh button for all their referred users
- [ ] **RBAC-07**: Regular users cannot trigger refresh for other users

### Display

- [ ] **DISP-01**: Census data displayed on user's own profile page (read-only)
- [ ] **DISP-02**: Census status indicator (pending, found, error, etc.)
- [ ] **DISP-03**: Leader's referidos page shows census data for referred users
- [ ] **DISP-04**: Bulk refresh button visible only to leaders on referidos page

## Future Requirements (v2+)

### Enhancements

- **ENH-01**: Proxy rotation if consistently blocked by F5
- **ENH-02**: Scheduled re-validation (periodic refresh)
- **ENH-03**: WebSocket real-time status updates
- **ENH-04**: Export census data to CSV/Excel
- **ENH-05**: Additional roles beyond USER/LEADER

## Out of Scope

| Feature | Reason |
|---------|--------|
| Editable census data | Data comes from official source, must be read-only |
| Real-time scraping in HTTP cycle | Blocks user request, bad UX |
| Unlimited retries | Would spam Registraduría, risk IP block |
| Complex anti-bot bypass | Diminishing returns, build for graceful failure |
| User self-promotion to Leader | Security risk, admin-only role assignment |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 | Phase 11 | Pending |
| INFRA-02 | Phase 11 | Pending |
| INFRA-03 | Phase 11 | Pending |
| INFRA-04 | Phase 11 | Pending |
| DATA-01 | Phase 12 | Pending |
| DATA-02 | Phase 12 | Pending |
| DATA-03 | Phase 12 | Pending |
| DATA-04 | Phase 12 | Pending |
| DATA-05 | Phase 12 | Pending |
| DATA-06 | Phase 12 | Pending |
| RBAC-01 | Phase 12 | Pending |
| RBAC-02 | Phase 12 | Pending |
| RBAC-03 | Phase 12 | Pending |
| SCRP-01 | Phase 13 | Pending |
| SCRP-02 | Phase 13 | Pending |
| SCRP-03 | Phase 13 | Pending |
| SCRP-04 | Phase 13 | Pending |
| SCRP-05 | Phase 13 | Pending |
| SCRP-06 | Phase 13 | Pending |
| SCRP-07 | Phase 13 | Pending |
| TRIG-01 | Phase 14 | Pending |
| TRIG-02 | Phase 14 | Pending |
| TRIG-03 | Phase 14 | Pending |
| RBAC-04 | Phase 15 | Pending |
| RBAC-05 | Phase 15 | Pending |
| RBAC-06 | Phase 15 | Pending |
| RBAC-07 | Phase 15 | Pending |
| DISP-01 | Phase 15 | Pending |
| DISP-02 | Phase 15 | Pending |
| DISP-03 | Phase 16 | Pending |
| DISP-04 | Phase 16 | Pending |

**Coverage:**
- v1.3 requirements: 29 total
- Mapped to phases: 29
- Unmapped: 0 ✓

---
*Requirements defined: 2026-01-19*
*Last updated: 2026-01-19 after initial definition*
