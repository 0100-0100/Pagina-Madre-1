# Phase 16: Referidos Page Updates - Context

**Gathered:** 2026-01-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Leaders see census data for all their referred users with bulk refresh capability. This phase adds census status display, checkbox-based bulk refresh, and expandable rows with location details to the existing referidos page. Individual refresh and profile display are complete from Phase 15.

</domain>

<decisions>
## Implementation Decisions

### Census status display
- Badge/pill format with Bootstrap semantic colors
  - success = found, warning = pending, danger = error, secondary = not found
- Distinct "Cancelada" badge for cancelled cedulas (not grouped with not_found)
- Spinner badge for PENDING/PROCESSING states
- Generic "Error" badge for all error types (no specific error labels)
- Table columns: Name + Cedula + Registration Date + Status

### Expandable row details
- Click row to expand/collapse detail row below
- Full location info when expanded: department, municipality, voting place, address
- Timestamp displayed in user's local time (stored UTC, rendered client-side via JavaScript)
- Per-referral refresh button visible only in expanded row
- Error message with hint: "Error al consultar — intenta de nuevo más tarde"

### Bulk refresh behavior
- Checkbox selection for individual referrals (no "select all" checkbox)
- Refresh button only visible for non-final statuses (ERROR, NOT_FOUND, PENDING)
- Hide refresh for FOUND and CANCELLED — validation complete
- Idempotent: don't create new task if one already running for that cedula
- Per-user cooldown only for error/not_found states
- Row-by-row update feedback (spinner on each row as it processes, no toast summary)

### RBAC and navigation
- Regular users: read-only table, no refresh capability, no navigation to other profiles
- Leaders/Admins/Superadmins: cedula is clickable link to user's profile (same tab)
- Breadcrumbs for navigation: "Referidos > Perfil de [nombre]" when viewing referral's profile

### Table interaction
- Clickable column headers for sorting
- Filter tabs: All | Pendientes | Encontrados | Errores (no counts on tabs)

### Empty state
- Message: "No tienes referidos aún"
- CTA: "Comparte tu código de referido" with copy button

### Claude's Discretion
- Exact breadcrumb styling and placement
- Sort order priority (which column sorted by default)
- Expandable row animation/transition
- Filter tab visual design

</decisions>

<specifics>
## Specific Ideas

- Timestamps must be stored in UTC and displayed in the user's browser local time for traceability across timezones
- Both bulk and single refresh should follow identical idempotent logic
- Row-by-row visual feedback during bulk operations (no aggregate toast)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 16-referidos-page-updates*
*Context gathered: 2026-01-21*
