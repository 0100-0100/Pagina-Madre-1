# Requirements: v1.3 Async Background Jobs

**Defined:** 2026-01-19
**Core Value:** Users can securely register and authenticate to access the portal.

## v1.3 Requirements

Requirements for v1.3 milestone. Each maps to roadmap phases.

### Infrastructure

- [x] **INFRA-01**: Django-Q2 task queue installed and configured with ORM broker — v1.3 Phase 11
- [x] **INFRA-02**: SQLite WAL mode enabled to prevent database locking — v1.3 Phase 11
- [x] **INFRA-03**: Task worker process (qcluster) runs successfully — v1.3 Phase 11
- [x] **INFRA-04**: Task timeout and retry configured (timeout=120s, retry=180s) — v1.3 Phase 11

### Scraping

- [x] **SCRP-01**: Playwright headless browser installed with Chromium — v1.3 Phase 13
- [x] **SCRP-02**: Stealth patches applied to avoid bot detection — v1.3 Phase 13 (minimal, structured for future)
- [x] **SCRP-03**: Scraper handles "active" response (voting location data) — v1.3 Phase 13
- [x] **SCRP-04**: Scraper handles "cancelled" response (deceased/novedad data) — v1.3 Phase 13
- [x] **SCRP-05**: Scraper handles "not found" response — v1.3 Phase 13
- [x] **SCRP-06**: Scraper handles errors gracefully (timeout, network, bot block) — v1.3 Phase 13
- [x] **SCRP-07**: Rate limiting between requests (minimum 5 seconds) — v1.3 Phase 13

### Data Model

- [x] **DATA-01**: CedulaInfo model created with OneToOne link to CustomUser — v1.3 Phase 12
- [x] **DATA-02**: Status field with 9 choices: PENDING, PROCESSING, ACTIVE, NOT_FOUND, CANCELLED_DECEASED, CANCELLED_OTHER, ERROR, TIMEOUT, BLOCKED — v1.3 Phase 12
- [x] **DATA-03**: Voting location fields: departamento, municipio, puesto, direccion, mesa — v1.3 Phase 12
- [x] **DATA-04**: Cancelled fields: novedad, resolucion, fecha_novedad — v1.3 Phase 12
- [x] **DATA-05**: Metadata fields: fetched_at, error_message, raw_response — v1.3 Phase 12
- [x] **DATA-06**: CedulaInfo registered in Django admin (read-only display) — v1.3 Phase 12

### Triggers

- [x] **TRIG-01**: Background task auto-triggers on user registration via post_save signal — v1.3 Phase 14
- [x] **TRIG-02**: Signal uses transaction.on_commit() to avoid race conditions — v1.3 Phase 14
- [x] **TRIG-03**: Retry logic with exponential backoff (max 3 attempts) — v1.3 Phase 14

### RBAC (Role-Based Access Control)

- [x] **RBAC-01**: Role field added to CustomUser with choices: USER, LEADER — v1.3 Phase 12
- [x] **RBAC-02**: Default role is USER for new registrations — v1.3 Phase 12
- [x] **RBAC-03**: Only Django superadmin can change user roles (via admin) — v1.3 Phase 12
- [x] **RBAC-04**: Leader can view census data for users they referred — v1.3 Phase 15
- [x] **RBAC-05**: Leader sees manual refresh button for individual referred users — v1.3 Phase 15
- [x] **RBAC-06**: Leader has bulk refresh button for all their referred users — v1.3 Phase 16
- [x] **RBAC-07**: Regular users cannot trigger refresh for other users — v1.3 Phase 15

### Display

- [x] **DISP-01**: Census data displayed on user's own profile page (read-only) — v1.3 Phase 15
- [x] **DISP-02**: Census status indicator (pending, found, error, etc.) — v1.3 Phase 15
- [x] **DISP-03**: Leader's referidos page shows census data for referred users — v1.3 Phase 16
- [x] **DISP-04**: Bulk refresh button visible only to leaders on referidos page — v1.3 Phase 16
- [x] **DISP-05**: Referidos page auto-updates when census data is fetched (HTMX polling) — v1.3 Phase 16

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
| Unlimited retries | Would spam Registraduria, risk IP block |
| Complex anti-bot bypass | Diminishing returns, build for graceful failure |
| User self-promotion to Leader | Security risk, admin-only role assignment |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 | Phase 11 | Complete |
| INFRA-02 | Phase 11 | Complete |
| INFRA-03 | Phase 11 | Complete |
| INFRA-04 | Phase 11 | Complete |
| DATA-01 | Phase 12 | Complete |
| DATA-02 | Phase 12 | Complete |
| DATA-03 | Phase 12 | Complete |
| DATA-04 | Phase 12 | Complete |
| DATA-05 | Phase 12 | Complete |
| DATA-06 | Phase 12 | Complete |
| RBAC-01 | Phase 12 | Complete |
| RBAC-02 | Phase 12 | Complete |
| RBAC-03 | Phase 12 | Complete |
| SCRP-01 | Phase 13 | Complete |
| SCRP-02 | Phase 13 | Complete |
| SCRP-03 | Phase 13 | Complete |
| SCRP-04 | Phase 13 | Complete |
| SCRP-05 | Phase 13 | Complete |
| SCRP-06 | Phase 13 | Complete |
| SCRP-07 | Phase 13 | Complete |
| TRIG-01 | Phase 14 | Complete |
| TRIG-02 | Phase 14 | Complete |
| TRIG-03 | Phase 14 | Complete |
| RBAC-04 | Phase 15 | Complete |
| RBAC-05 | Phase 15 | Complete |
| RBAC-06 | Phase 16 | Complete |
| RBAC-07 | Phase 15 | Complete |
| DISP-01 | Phase 15 | Complete |
| DISP-02 | Phase 15 | Complete |
| DISP-03 | Phase 16 | Complete |
| DISP-04 | Phase 16 | Complete |
| DISP-05 | Phase 16 | Complete |

**Coverage:**
- v1.3 requirements: 32 total
- Mapped to phases: 32
- Unmapped: 0 ✓

---
*Requirements defined: 2026-01-19*
*Last updated: 2026-01-21 after Phase 16 completion (v1.3 Complete)*
