# Phase 16: Referidos Page Updates - Research

**Researched:** 2026-01-21
**Domain:** Django views, HTMX tables/polling, Bootstrap 5 UI, expandable rows, bulk operations
**Confidence:** HIGH

## Summary

This phase extends the existing referidos page with census status display, expandable detail rows, bulk refresh capability, and filter tabs. The implementation builds directly on Phase 15 patterns: HTMX 2.0.4 via CDN, Bootstrap 5.3.8 badges/cards, the `leader_or_self_required` decorator, and `_census_section.html` partial rendering.

The key additions are: (1) expandable table rows for location details using `aria-expanded` and display toggle, (2) checkbox selection for bulk refresh with HTMX form submission, (3) client-side JavaScript filter tabs for status filtering, and (4) row-level spinner indicators during individual refresh operations. Client-side timestamp conversion uses the native JavaScript Date API with `toLocaleString()`.

**Primary recommendation:** Extend the existing referidos.html with HTMX-powered partials for each referral row. Use JavaScript for expand/collapse and filtering (no HTMX needed for these client-side operations). Bulk refresh submits selected checkboxes via HTMX POST form.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| HTMX | 2.0.4 | Bulk refresh, row-level updates, polling | Already in project from Phase 15 |
| Bootstrap 5 | 5.3.8 | Badges, tabs, tables, spinners | Already in project |
| Django | 4.2.x | Views, templates, ORM | Already in project |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| django.contrib.humanize | built-in | naturaltime filter | Server-side fallback timestamps |
| JavaScript Date API | native | Client-side UTC to local | Displaying timestamps in user's timezone |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| JS Date for timestamps | moment.js/luxon | Extra dependency, native API sufficient |
| Client-side filtering | Server-side HTMX tabs | Extra requests, client-side is faster |
| JavaScript expand/collapse | HTMX hx-get for details | Over-engineering, pure JS is simpler |
| Inline checkboxes | Alpine.js for reactivity | Extra dependency, vanilla JS works fine |

**Installation:**
```bash
# No additional pip install needed - all dependencies already in project
```

## Architecture Patterns

### Recommended Project Structure
```
templates/
├── referidos.html                    # Main page (extend existing)
└── partials/
    ├── _referral_row.html            # Single referral table row
    └── _referral_detail.html         # Expandable detail content
accounts/
├── views.py                          # Add bulk_refresh_view, referral_row_view
├── urls.py                           # Add new endpoints
└── decorators.py                     # leader_or_self_required (existing)
```

### Pattern 1: Expandable Table Row with Accessibility
**What:** Click row to toggle detail row visibility with proper ARIA attributes
**When to use:** Showing location details without cluttering main table
**Example:**
```html
<!-- Source: https://adrianroselli.com/2019/09/table-with-expando-rows.html -->
<tr id="row-{{ referral.id }}" class="referral-row"
    onclick="toggleDetail({{ referral.id }})"
    style="cursor: pointer;">
    <td>
        <button type="button" class="btn btn-link p-0"
                aria-expanded="false"
                aria-controls="detail-{{ referral.id }}"
                aria-label="Ver detalles">
            <i class="bi bi-chevron-right toggle-icon"></i>
        </button>
        {{ referral.nombre_completo }}
    </td>
    <td>{{ referral.cedula }}</td>
    <td>{{ referral.date_joined|date:"Y-m-d" }}</td>
    <td>{% include 'partials/_status_badge.html' %}</td>
</tr>
<tr id="detail-{{ referral.id }}" class="detail-row" style="display: none;">
    <td colspan="4">
        <!-- Location details, refresh button -->
    </td>
</tr>
```

### Pattern 2: Checkbox Bulk Selection with HTMX Form
**What:** Form wraps table, checkboxes encode referral IDs, button submits checked items
**When to use:** Bulk refresh of multiple referrals
**Example:**
```html
<!-- Source: https://htmx.org/examples/bulk-update/ -->
<form id="bulk-refresh-form"
      hx-post="{% url 'bulk_refresh' %}"
      hx-target="#toast-container"
      hx-swap="innerHTML"
      hx-indicator="#bulk-indicator">
    {% csrf_token %}
    <table class="table">
        <tbody>
            {% for referral in referrals %}
            <tr>
                <td>
                    {% if referral.can_refresh %}
                    <input type="checkbox" name="ids" value="{{ referral.id }}"
                           class="form-check-input referral-checkbox">
                    {% endif %}
                </td>
                <!-- other columns -->
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <button type="submit" class="btn btn-primary"
            hx-disabled-elt="this"
            id="bulk-refresh-btn">
        <span class="htmx-indicator" id="bulk-indicator">
            <span class="spinner-border spinner-border-sm"></span>
        </span>
        <span class="htmx-indicator-hide">Actualizar Seleccionados</span>
    </button>
</form>
```

### Pattern 3: Client-Side UTC to Local Timestamp
**What:** Server sends UTC, JavaScript converts to user's local timezone
**When to use:** Displaying fetched_at timestamp in referral details
**Example:**
```html
<!-- Source: https://bobbyhadz.com/blog/javascript-convert-utc-to-local-time -->
<span class="local-time" data-utc="{{ cedula_info.fetched_at|date:'c' }}">
    <!-- JS will populate -->
</span>

<script>
document.querySelectorAll('.local-time').forEach(el => {
    const utc = el.dataset.utc;
    if (utc) {
        const date = new Date(utc);
        el.textContent = date.toLocaleString('es-CO', {
            dateStyle: 'short',
            timeStyle: 'short'
        });
    }
});
</script>
```

### Pattern 4: Client-Side Filter Tabs
**What:** Bootstrap nav-pills filter table rows by data attribute
**When to use:** All | Pendientes | Encontrados | Errores tabs
**Example:**
```html
<ul class="nav nav-pills mb-3">
    <li class="nav-item">
        <button class="nav-link active" data-filter="all">Todos</button>
    </li>
    <li class="nav-item">
        <button class="nav-link" data-filter="pending">Pendientes</button>
    </li>
    <li class="nav-item">
        <button class="nav-link" data-filter="found">Encontrados</button>
    </li>
    <li class="nav-item">
        <button class="nav-link" data-filter="error">Errores</button>
    </li>
</ul>

<script>
document.querySelectorAll('[data-filter]').forEach(btn => {
    btn.addEventListener('click', () => {
        const filter = btn.dataset.filter;
        document.querySelectorAll('.referral-row').forEach(row => {
            const status = row.dataset.status;
            if (filter === 'all' || status === filter) {
                row.style.display = '';
                // Also show/hide associated detail row if expanded
            } else {
                row.style.display = 'none';
            }
        });
        // Update active tab
        document.querySelectorAll('[data-filter]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    });
});
</script>
```

### Pattern 5: Row-Level Spinner Indicator
**What:** Each row shows its own spinner during individual refresh
**When to use:** Per-referral refresh button in expanded detail row
**Example:**
```html
<!-- Source: https://htmx.org/attributes/hx-indicator/ -->
<button hx-post="{% url 'refresh_cedula_user' referral.id %}"
        hx-target="#row-{{ referral.id }}"
        hx-swap="outerHTML"
        hx-indicator="#spinner-{{ referral.id }}"
        hx-disabled-elt="this"
        class="btn btn-sm btn-outline-secondary">
    <span id="spinner-{{ referral.id }}" class="htmx-indicator">
        <span class="spinner-border spinner-border-sm"></span>
    </span>
    <span class="htmx-indicator-hide">
        <i class="bi bi-arrow-clockwise"></i>
    </span>
    Actualizar
</button>
```

### Pattern 6: Sortable Table Headers (Client-Side)
**What:** Click column header to sort table rows
**When to use:** Name, cedula, date, status columns
**Example:**
```html
<th class="sortable" data-sort="name" onclick="sortTable('name')">
    Nombre <i class="bi bi-arrow-down-up"></i>
</th>

<script>
let sortDirection = {};
function sortTable(column) {
    const tbody = document.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('.referral-row'));
    sortDirection[column] = !sortDirection[column]; // Toggle

    rows.sort((a, b) => {
        const aVal = a.dataset[column] || '';
        const bVal = b.dataset[column] || '';
        return sortDirection[column]
            ? aVal.localeCompare(bVal)
            : bVal.localeCompare(aVal);
    });

    // Re-append rows (includes their detail rows)
    rows.forEach(row => {
        tbody.appendChild(row);
        const detailRow = document.getElementById('detail-' + row.dataset.id);
        if (detailRow) tbody.appendChild(detailRow);
    });
}
</script>
```

### Anti-Patterns to Avoid
- **Using HTMX for expand/collapse:** Over-engineering; pure JS is simpler for local state
- **Server-side filtering for small datasets:** Extra latency; client-side is instant
- **Polling all rows at once:** Poll only the bulk-refresh result area, not individual rows
- **Missing colspan on detail rows:** Breaks table layout
- **Using display:block on hidden rows:** Breaks table semantics; use display:none/table-row
- **Select-all checkbox without idempotency:** Can lead to re-queueing tasks already running

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| UTC to local time | Custom date math | `new Date(utc).toLocaleString()` | Handles DST, locale, all edge cases |
| Row expand animation | CSS transitions on height | `display: none/table-row` toggle | Height animation on tr is buggy |
| Bulk checkbox tracking | Custom state management | Form with `name="ids"` checkboxes | HTMX sends only checked values automatically |
| Sort direction indicators | Custom icon toggle | CSS `::after` with data attribute | Cleaner, more maintainable |
| Refresh cooldown client-side | setInterval countdown | Server-side 30s check | More secure, single source of truth |

**Key insight:** The referidos page can use client-side JavaScript for expand/collapse, filtering, and sorting. HTMX is only needed for actual server communication (refresh operations). Don't use HTMX where vanilla JS suffices.

## Common Pitfalls

### Pitfall 1: Detail Row Lost on Sort
**What goes wrong:** After sorting, detail rows appear in wrong positions or disappear
**Why it happens:** Sort only moves `.referral-row` elements, not associated detail rows
**How to avoid:** Move both the main row and its detail row together when sorting
**Warning signs:** Clicking expand after sort shows wrong user's details

### Pitfall 2: Filter Hides Expanded Details
**What goes wrong:** Filtering hides a row but leaves its expanded detail visible
**Why it happens:** Filter only toggles `.referral-row`, forgets `.detail-row`
**How to avoid:** When hiding a row, also collapse and hide its detail row
**Warning signs:** Orphaned detail content visible after filtering

### Pitfall 3: Bulk Refresh Overwhelms Server
**What goes wrong:** User selects 50 referrals, triggers 50 concurrent tasks
**Why it happens:** No batch limit, no queue awareness
**How to avoid:** Server-side limit (e.g., max 10 per request); skip already-processing cedulas
**Warning signs:** Task queue backlog, timeouts

### Pitfall 4: Checkbox State Lost on HTMX Swap
**What goes wrong:** After row HTMX update, checkbox checked state resets
**Why it happens:** HTMX replaces entire row including checkbox
**How to avoid:** Either preserve checkbox outside swap target, or re-check via JS after swap
**Warning signs:** User checks box, clicks individual refresh, checkbox unchecks

### Pitfall 5: Accessibility Issues with Expandable Rows
**What goes wrong:** Screen readers can't navigate expanded content
**Why it happens:** Missing ARIA attributes, improper focus management
**How to avoid:** Use `aria-expanded`, `aria-controls`, and `display:table-row` (not block)
**Warning signs:** WAVE or axe audit failures

### Pitfall 6: Clicking Row Accidentally Triggers Navigation
**What goes wrong:** Leader clicks row to expand, but cedula link navigates away
**Why it happens:** Click event bubbles from link to row
**How to avoid:** Stop propagation on link clicks, or use separate expand button column
**Warning signs:** Users complain about unexpected navigation

## Code Examples

Verified patterns from official sources and project context:

### Status Badge Mapping (Bootstrap 5)
```html
{% if cedula_info.status == 'ACTIVE' %}
    <span class="badge bg-success"><i class="bi bi-check-circle"></i> Encontrado</span>
{% elif cedula_info.status == 'PENDING' or cedula_info.status == 'PROCESSING' %}
    <span class="badge bg-warning text-dark">
        <span class="spinner-border spinner-border-sm"></span> Pendiente
    </span>
{% elif cedula_info.status == 'NOT_FOUND' %}
    <span class="badge bg-secondary"><i class="bi bi-question-circle"></i> No encontrado</span>
{% elif cedula_info.status == 'CANCELLED_DECEASED' or cedula_info.status == 'CANCELLED_OTHER' %}
    <span class="badge bg-secondary"><i class="bi bi-dash-circle"></i> Cancelada</span>
{% elif cedula_info.status in 'ERROR,TIMEOUT,BLOCKED' %}
    <span class="badge bg-danger"><i class="bi bi-x-circle"></i> Error</span>
{% else %}
    <span class="badge bg-secondary">{{ cedula_info.get_status_display }}</span>
{% endif %}
```

### Refresh Button Visibility Logic (Django Template)
```html
{% with status=referral.cedula_info.status %}
    {% if status != 'ACTIVE' and status != 'CANCELLED_DECEASED' and status != 'CANCELLED_OTHER' %}
        <!-- Show refresh button - status is ERROR, NOT_FOUND, PENDING, etc. -->
        <button hx-post="{% url 'refresh_cedula_user' referral.id %}" ...>
            Actualizar
        </button>
    {% endif %}
{% endwith %}
```

### Empty State with Copy CTA
```html
{% if not referrals %}
<div class="text-center py-5">
    <i class="bi bi-people display-1 text-muted mb-3 d-block"></i>
    <h5 class="text-muted mb-2">No tienes referidos aun</h5>
    <p class="text-muted mb-4">Comparte tu codigo de referido para empezar</p>
    <div class="input-group mb-3 justify-content-center" style="max-width: 400px; margin: 0 auto;">
        <input type="text" class="form-control" value="{{ referral_url }}" readonly id="referral-url">
        <button class="btn btn-primary" onclick="copyReferralUrl()">
            <i class="bi bi-clipboard"></i> Copiar
        </button>
    </div>
</div>

<script>
function copyReferralUrl() {
    const input = document.getElementById('referral-url');
    navigator.clipboard.writeText(input.value);
    // Show toast or change button text
}
</script>
{% endif %}
```

### Breadcrumb Navigation (Leaders viewing referral profile)
```html
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="{% url 'referidos' %}">Referidos</a></li>
        <li class="breadcrumb-item active" aria-current="page">
            Perfil de {{ target_user.nombre_completo }}
        </li>
    </ol>
</nav>
```

### Bulk Refresh View (Django)
```python
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django_q.tasks import async_task

@login_required
@require_POST
def bulk_refresh_view(request):
    """Bulk refresh cedula for selected referrals."""
    if request.user.role != CustomUser.Role.LEADER:
        return HttpResponseForbidden("Solo lideres pueden hacer esto.")

    ids = request.POST.getlist('ids')
    if not ids:
        return render(request, 'partials/_toast.html', {
            'message': 'No hay referidos seleccionados',
            'type': 'warning'
        })

    # Limit to max 10 per request
    ids = ids[:10]

    # Get valid referrals (must be referred by this leader)
    referrals = CustomUser.objects.filter(
        id__in=ids,
        referred_by=request.user
    ).select_related('cedula_info')

    refreshed = 0
    for referral in referrals:
        cedula_info = getattr(referral, 'cedula_info', None)
        # Skip if already processing or found/cancelled
        if cedula_info and cedula_info.status in ['ACTIVE', 'CANCELLED_DECEASED', 'CANCELLED_OTHER', 'PROCESSING']:
            continue
        if cedula_info:
            cedula_info.status = CedulaInfo.Status.PROCESSING
            cedula_info.save(update_fields=['status'])
        async_task('accounts.tasks.validate_cedula', referral.id, 1)
        refreshed += 1

    response = render(request, 'partials/_toast.html', {
        'message': f'{refreshed} cedulas en actualizacion',
        'type': 'info'
    })
    response['HX-Trigger'] = 'refreshComplete'
    return response
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| DataTables.js for sorting | Vanilla JS + CSS | 2023+ | Smaller bundle, no jQuery dependency |
| moment.js for dates | Native Date + toLocaleString | ES6 (2015+) | No dependency, browser handles i18n |
| Server-side tab filtering | Client-side JS filtering | Always valid | Instant UX for small datasets |
| Alpine.js for checkboxes | Vanilla JS + HTMX forms | HTMX 2.0 | One less dependency |

**Deprecated/outdated:**
- jQuery DataTables (heavy, not needed for simple sort/filter)
- moment.js (larger than needed, native API now sufficient)
- Server-side pagination for <100 rows (client-side is faster)

## Open Questions

Things that couldn't be fully resolved:

1. **Checkbox state preservation after row swap**
   - What we know: HTMX replaces the entire row on individual refresh
   - What's unclear: Best pattern to preserve checkbox state
   - Recommendation: Either target only the status column, or use `htmx:afterSwap` event to restore checkbox state

2. **Maximum referrals before pagination needed**
   - What we know: Client-side works well for ~50-100 rows
   - What's unclear: At what point server-side pagination is necessary
   - Recommendation: Implement server-side pagination as Phase 17 if user testing shows performance issues

3. **Bulk refresh progress indication**
   - What we know: User decision was "row-by-row update feedback, no toast summary"
   - What's unclear: How to show progress when tasks complete asynchronously
   - Recommendation: Each row polls independently for status after bulk trigger; disable checkboxes for PROCESSING rows

## Sources

### Primary (HIGH confidence)
- [HTMX Bulk Update Example](https://htmx.org/examples/bulk-update/) - Form with checkboxes pattern
- [HTMX hx-indicator Documentation](https://htmx.org/attributes/hx-indicator/) - Row-level spinners, `closest` selector
- [Bootstrap 5.3 Navs and Tabs](https://getbootstrap.com/docs/5.3/components/navs-tabs/) - Pills styling
- [Accessible Expando Rows - Adrian Roselli](https://adrianroselli.com/2019/09/table-with-expando-rows.html) - ARIA attributes, semantic HTML
- Phase 15 RESEARCH.md (project) - Established HTMX, polling, toast patterns

### Secondary (MEDIUM confidence)
- [Bootstrap 5 Tabs with HTMX - Marcus Obst](https://marcus-obst.de/blog/use-bootstrap-5x-tabs-with-htmx) - Integration patterns
- [JavaScript UTC to Local - bobbyhadz](https://bobbyhadz.com/blog/javascript-convert-utc-to-local-time) - toLocaleString approach
- [HTMX HX-Trigger Headers](https://htmx.org/headers/hx-trigger/) - Event triggering from server

### Tertiary (LOW confidence)
- [Bootstrap-sortable GitHub](https://github.com/drvic10k/bootstrap-sortable) - Alternative if vanilla JS sorting insufficient
- WebSearch results for bulk actions patterns - May need validation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries already in project from Phase 15
- Architecture: HIGH - Patterns verified against HTMX docs and project patterns
- Pitfalls: HIGH - Based on existing Phase 15 experience and documented HTMX issues
- Code examples: MEDIUM - Some patterns adapted from docs, need testing

**Research date:** 2026-01-21
**Valid until:** 2026-03-21 (60 days - stable stack, extends Phase 15 patterns)
