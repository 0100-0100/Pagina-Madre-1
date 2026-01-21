# Phase 15: Profile Display + Refresh - Context

**Gathered:** 2026-01-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Users see their census data on their profile page; leaders can trigger manual refresh for themselves and their referrals. This phase covers display and refresh actions only — the referidos page census columns are Phase 16.

</domain>

<decisions>
## Implementation Decisions

### Census Status Display
- Pending state: Animated spinner icon with "Verificando cédula..." text
- Found state: Green "Verificado" badge followed by voting location details
- Error states: Color-coded badges — red for scraper errors, orange for not_found, gray for cancelled — each with brief explanation text
- Timestamp: Always show last validation timestamp (e.g., "Verificado: 20 ene 2026" or "Pendiente desde: hace 5 min")

### Voting Location Presentation
- Show all fields: Departamento, Municipio, Puesto de votación, Dirección
- Layout: Stacked labels — each field on its own line with label (e.g., "Departamento: Cundinamarca")
- Grouping: Badge and location details in same card/section
- Section title: "Datos Electorales"

### Refresh Button UX
- Placement: Inside the census section (small refresh button next to or below census data)
- Access control: Leaders only — regular users cannot manually refresh
- Referral refresh: Individual refresh buttons per user (no bulk refresh — that's Phase 16)
- Button style: Icon + text ("Actualizar" with refresh icon)

### Feedback During Refresh
- Immediate: Button becomes spinner and disables until task completes
- Completion: HTMX polls and auto-updates census section when task finishes
- Errors: Both toast notification AND badge reflects final error state
- Rate limiting: 30-second cooldown after click (button disabled)

### Claude's Discretion
- Exact spinner animation style
- Toast notification positioning and styling
- HTMX polling interval
- Specific Spanish text for error messages

</decisions>

<specifics>
## Specific Ideas

- Status badges should follow Bootstrap color conventions (success=green, danger=red, warning=orange, secondary=gray)
- The "Datos Electorales" section should feel like a cohesive card within the profile
- Refresh button should be subtle but discoverable for leaders

</specifics>

<deferred>
## Deferred Ideas

- Bulk refresh for all referrals — Phase 16 (referidos page)
- Census status column in referidos table — Phase 16

</deferred>

---

*Phase: 15-profile-display-refresh*
*Context gathered: 2026-01-20*
