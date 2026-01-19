# Phase 9: Profile Page - Context

**Gathered:** 2026-01-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Users can manage their account details and set their referral goal. This phase builds the profile page with editable fields (nombre, teléfono, meta de referidos) and a link to a separate password change page. The profile page replaces the placeholder route created in Phase 8.

</domain>

<decisions>
## Implementation Decisions

### Form layout & sections
- Single form card containing all fields
- Centered medium width card (same style as home page, 50-60%)
- Field order: Cédula (read-only), Nombre, Teléfono, Meta de referidos, then "Cambiar Contraseña" button
- Cédula displayed as read-only text (not editable - it's the username)

### Password change flow
- Password change on separate dedicated page (/cambiar-password/ or similar)
- Requires current password + new password + confirm new password
- Link from profile: "Cambiar Contraseña" button (btn-outline-secondary style)
- After successful change: redirect back to profile with success message (toast)

### Save behavior & feedback
- Single "Guardar" button at bottom of form saves all fields together
- Success feedback: Toast notification (same style as copy button - top-right)
- Error feedback: Both inline errors per field (red text below) + summary alert at top
- Button position: Bottom of form (not sticky)

### Field validation
- Real-time validation with debounce (same style as register page)
- Input filtering applied:
  - Nombre: letters and accents only
  - Teléfono: numbers only
  - Meta de referidos: numbers only (0 or higher allowed)
- Required fields: Nombre and Teléfono (cannot be empty)
- Meta de referidos: Any positive number (0 or higher)

### Claude's Discretion
- Exact field labels (Spanish)
- Debounce timing (can match register page's 1.5s)
- Button styling details
- Password page layout/styling

</decisions>

<specifics>
## Specific Ideas

- Profile card should match home page card style for visual consistency
- Toast notification should use same pattern implemented for copy button feedback
- Input filtering should reuse patterns from register page (letters+accents for nombre, numeric for phone)
- Password change can use Django's built-in PasswordChangeView as noted in research

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 09-profile-page*
*Context gathered: 2026-01-19*
