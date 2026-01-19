# Phase 8: Home Page Referral UI - Context

**Gathered:** 2026-01-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Users can see their referral progress and share their unique link from the home page. This phase adds referral stats display, a copy-to-clipboard button for the referral link, and navigation links to Perfil and Referidos pages. The actual Perfil and Referidos pages are built in separate phases.

</domain>

<decisions>
## Implementation Decisions

### Referral stats display
- Big number prominently displayed: "X referidos"
- Progress bar below showing progress toward goal (Bootstrap default style, blue fill)
- Text showing "X de Y referidos" with the progress bar
- Empty state (0 referrals): Show "0 referidos" with empty progress bar + encouragement text "¡Comparte tu enlace!"

### Shareable link presentation
- Link is NOT visible on the page
- Single button with text "Copiar Link de Referido"
- Button style: Bootstrap btn-primary with clipboard/copy icon next to text
- On click: Copy full referral URL to clipboard
- Visual feedback after copying:
  - Button text changes to "¡Copiado!" for 2 seconds, then reverts
  - Toast notification appears top-right: "Enlace copiado al portapapeles"

### Navigation to new pages
- Links placed in navbar on right side, before logout button
- Separate links (not dropdown): Perfil | Referidos | Logout
- Each link has icon + text label
- Icons: User icon for Perfil, people/group icon for Referidos

### Layout & visual hierarchy
- Two separate Bootstrap cards, vertically stacked
- Order: Stats card first (top), Share card second (bottom)
- Cards are centered, medium width (50-60% of container)
- Stats card contains: big referral count, progress bar, goal text
- Share card contains: copy button

### Claude's Discretion
- Exact spacing and padding values
- Specific Bootstrap icon choices (from Bootstrap Icons)
- Toast auto-dismiss timing
- Card header text (if any)

</decisions>

<specifics>
## Specific Ideas

- Copy button should feel like a clear call-to-action (primary blue, prominent)
- Progress bar uses standard Bootstrap styling (no custom colors)
- Encouragement text for zero referrals should motivate sharing

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 08-home-page-referral-ui*
*Context gathered: 2026-01-19*
