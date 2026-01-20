# Phase 12: CedulaInfo Model + RBAC - Context

**Gathered:** 2026-01-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Create CedulaInfo model to store census/voting data fetched from Registraduría, and add role field to CustomUser for USER/LEADER distinction. This phase creates the data structures; displaying and using the data is handled in later phases.

</domain>

<decisions>
## Implementation Decisions

### Status Choices
- Use granular statuses for full visibility:
  - `PENDING` — Task queued but not yet processed
  - `PROCESSING` — Task currently running
  - `ACTIVE` — Valid cédula with voting location
  - `NOT_FOUND` — Cédula not in electoral census
  - `CANCELLED_DECEASED` — Cédula cancelled due to death
  - `CANCELLED_OTHER` — Cédula cancelled for other reasons (suspended, invalid)
  - `ERROR` — General scraping error
  - `TIMEOUT` — Scraping timed out
  - `BLOCKED` — Bot detection blocked the request

### Role Behavior
- Two roles: `USER` (default) and `LEADER`
- Role is separate from referrer status (having referrals doesn't auto-grant LEADER)
- Only Django superadmin can change roles (via admin)
- LEADER capabilities (for later phases):
  - View census data for users they referred
  - Refresh individual referral's census data
  - Bulk refresh all referrals' census data
- USER capabilities:
  - View their own census data on profile
- CSV/Excel bulk upload deferred to future milestone

### Admin Display
- CedulaInfo as separate admin model (not inline with User)
- CedulaInfo is read-only (no manual edits — data from scraping only)
- CedulaInfo list view shows all fields: User, Status, Departamento, Municipio, Puesto, Direccion, Mesa, Novedad, Resolucion, Fecha Novedad, Fetched At, Error Message, Raw Response
- User admin shows role column in list view

### Claude's Discretion
- Field ordering in model
- Admin list_filter and search_fields configuration
- Migration strategy for adding role field to existing users

</decisions>

<specifics>
## Specific Ideas

- Status choices should cover the full lifecycle: queued → processing → result (success/error variants)
- Raw response storage for debugging when scraping issues arise
- Role field should use Django's choices pattern with constants

</specifics>

<deferred>
## Deferred Ideas

- CSV/Excel bulk upload for leaders — future milestone
- Additional roles beyond USER/LEADER — future milestone
- CedulaInfo inline on User detail page — keep separate for now

</deferred>

---

*Phase: 12-cedulainfo-model-rbac*
*Context gathered: 2026-01-19*
