# Phase 15: Profile Display + Refresh - Research

**Researched:** 2026-01-21
**Domain:** Django views, HTMX polling/partial rendering, Bootstrap 5 UI, RBAC
**Confidence:** HIGH

## Summary

This phase focuses on displaying census data on user profiles and enabling leaders to trigger manual refresh of cedula validation. The implementation builds on existing patterns: Django function-based views, Bootstrap 5 cards, and the CedulaInfo model created in Phase 12. The new component is HTMX for progressive enhancement (polling, partial updates, button disabling during requests).

The standard approach uses HTMX via CDN (no django-htmx package needed for this scope), with partial template rendering for the census section. This allows the profile page to auto-update when validation completes without full page reloads. The refresh button will trigger an async task and disable itself during the request using HTMX's `hx-disabled-elt` attribute.

**Primary recommendation:** Use HTMX 2.0 via CDN with inline partials (define census section once, render conditionally). No need for django-htmx middleware for this simple use case.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| HTMX | 2.0.4 | Progressive enhancement | De facto standard for server-rendered dynamic UIs |
| Bootstrap 5 | 5.3.8 | Styling (already in project) | Consistent with existing UI |
| Django | 4.2.x | Views/templates | Already in project |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| django.contrib.humanize | built-in | naturaltime filter | Relative timestamps ("hace 5 min") |
| django-htmx | 1.27.0 | Optional middleware | Only if need `request.htmx` detection |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| HTMX polling | WebSockets | Overkill for <100 users, simpler is better |
| Inline partials | django-template-partials | Extra dependency, inline works fine |
| CDN HTMX | npm/bundled | Adds build step, CDN simpler for this project |

**Installation:**
```bash
# No additional pip install needed - HTMX loaded via CDN
# Optional: pip install django-htmx  # Only if middleware needed later
```

**Base template addition:**
```html
<!-- In base.html head, after Bootstrap -->
<script src="https://unpkg.com/htmx.org@2.0.4"
        integrity="sha384-HGfztofotfshcF7+8n44JQL2oJmowVChPTg48S+jvZoztPfvwD79OC/LTtG6dMp+"
        crossorigin="anonymous"></script>
```

## Architecture Patterns

### Recommended Project Structure
```
templates/
├── base.html                    # Add HTMX script
├── profile.html                 # Existing, add census section
└── partials/
    └── _census_section.html     # New partial (HTMX swappable)
accounts/
├── views.py                     # Add census_section_view, refresh_cedula_view
└── urls.py                      # Add new endpoints
```

### Pattern 1: Inline Partial Template
**What:** Define the census section in profile.html, extract to separate template for HTMX
**When to use:** When partial needs both full-page and HTMX render contexts
**Example:**
```django
{# templates/partials/_census_section.html #}
<div id="census-section" hx-get="{% url 'census_section' %}"
     hx-trigger="every 5s [{{ cedula_info.status }} == 'PENDING' or {{ cedula_info.status }} == 'PROCESSING']"
     hx-swap="outerHTML">
    {% if cedula_info.status == 'PENDING' or cedula_info.status == 'PROCESSING' %}
        <div class="d-flex align-items-center">
            <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <span>Verificando cedula...</span>
        </div>
    {% elif cedula_info.status == 'ACTIVE' %}
        <span class="badge bg-success">Verificado</span>
        {# voting location details #}
    {% endif %}
</div>
```

### Pattern 2: Conditional Template Rendering
**What:** View returns full page or partial based on request headers
**When to use:** HTMX requests need only the partial, full requests need complete page
**Example:**
```python
# Source: django-htmx documentation
def census_section_view(request):
    user = request.user
    cedula_info = getattr(user, 'cedula_info', None)

    # Check for HTMX request header
    is_htmx = request.headers.get('HX-Request') == 'true'

    if is_htmx:
        template = 'partials/_census_section.html'
    else:
        template = 'profile.html'

    return render(request, template, {'cedula_info': cedula_info})
```

### Pattern 3: Role-Based View Protection
**What:** Custom decorator checks user role before allowing access
**When to use:** Refresh endpoint for leaders only
**Example:**
```python
from functools import wraps
from django.http import HttpResponseForbidden

def leader_required(view_func):
    """Decorator to restrict view to LEADER role users."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'LEADER':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("No tienes permiso para esta accion.")
    return _wrapped_view
```

### Pattern 4: HTMX Button Disable During Request
**What:** Button disabled while async request in flight
**When to use:** Prevent double-submit on refresh button
**Example:**
```html
<button hx-post="{% url 'refresh_cedula' user.id %}"
        hx-target="#census-section"
        hx-swap="outerHTML"
        hx-disabled-elt="this"
        class="btn btn-sm btn-outline-secondary">
    <i class="bi bi-arrow-clockwise htmx-indicator-hide"></i>
    <span class="spinner-border spinner-border-sm htmx-indicator" style="display:none"></span>
    Actualizar
</button>
```

### Anti-Patterns to Avoid
- **Polling without conditions:** Always add conditional to stop when status is final
- **Full page refresh for partial update:** Use HTMX swap, not redirect
- **Hardcoded role checks:** Use decorator or mixin, not inline if statements
- **Missing CSRF on HTMX POST:** Always include `hx-headers` with csrf token

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Relative timestamps | Custom date formatting | `django.contrib.humanize.naturaltime` | Already localized, handles edge cases |
| Button disable during request | Custom JS with fetch | HTMX `hx-disabled-elt="this"` | Built-in, no JS needed |
| Polling with conditions | setInterval + fetch | HTMX `hx-trigger="every Ns [condition]"` | Built-in, cleaner |
| Stop polling on completion | Custom status checks | HTTP 286 response code | HTMX standard pattern |
| Toast notifications | Custom toast implementation | Bootstrap Toast + HX-Trigger header | Leverage existing Bootstrap |
| Role checking in views | Inline if statements | `@leader_required` decorator | Reusable, testable |

**Key insight:** HTMX handles most interactive patterns declaratively. The JS-heavy approach (fetch, setInterval, manual DOM updates) is unnecessary and harder to maintain.

## Common Pitfalls

### Pitfall 1: Polling Doesn't Stop
**What goes wrong:** Census section keeps polling even after status is final (ACTIVE, ERROR, etc.)
**Why it happens:** Missing or incorrect condition in `hx-trigger`
**How to avoid:** Use JavaScript condition in trigger: `hx-trigger="every 5s [statusIsPending]"` where `statusIsPending` is a JS variable or expression
**Warning signs:** Network tab shows continuous requests after validation completes

### Pitfall 2: CSRF Token Missing on HTMX POST
**What goes wrong:** 403 Forbidden on refresh button click
**Why it happens:** HTMX POST doesn't include CSRF token automatically
**How to avoid:** Add `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'` on body or form
**Warning signs:** First HTMX POST fails with 403

### Pitfall 3: Race Condition on Refresh
**What goes wrong:** User clicks refresh, task starts, but CedulaInfo status shows stale data
**Why it happens:** View reads status before task updates it
**How to avoid:** Set status to PROCESSING in view before returning, then let polling pick up final status
**Warning signs:** Brief flash of old status after refresh click

### Pitfall 4: Leader Refreshing Non-Referral User
**What goes wrong:** Leader can refresh any user's cedula, not just their referrals
**Why it happens:** Only checking if user is LEADER, not checking referral relationship
**How to avoid:** Verify `target_user.referred_by == request.user` in view
**Warning signs:** Security audit shows unauthorized access

### Pitfall 5: Cooldown Not Enforced Server-Side
**What goes wrong:** Malicious user bypasses client-side cooldown via curl
**Why it happens:** Only disabling button client-side, no server-side rate limit
**How to avoid:** Check `cedula_info.fetched_at` and enforce 30s minimum gap server-side
**Warning signs:** Rapid-fire requests in server logs

## Code Examples

Verified patterns from official sources:

### HTMX Polling with Conditional
```html
<!-- Source: https://htmx.org/attributes/hx-trigger/ -->
<div id="census-section"
     hx-get="{% url 'census_section' %}"
     hx-trigger="every 5s [document.querySelector('#census-status').dataset.polling === 'true']"
     hx-swap="outerHTML">
    <span id="census-status" data-polling="{{ is_polling|yesno:'true,false' }}">
        {# content #}
    </span>
</div>
```

### Bootstrap 5 Spinner in Button
```html
<!-- Source: https://getbootstrap.com/docs/5.3/components/spinners/ -->
<button class="btn btn-primary" type="button" disabled>
    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
    <span class="visually-hidden">Cargando...</span>
</button>
```

### HTMX Disabled Element During Request
```html
<!-- Source: https://htmx.org/attributes/hx-disabled-elt/ -->
<button hx-post="/refresh" hx-disabled-elt="this">
    Actualizar
</button>
```

### Django naturaltime for Spanish
```python
# settings.py
LANGUAGE_CODE = 'es'  # Enable Spanish
USE_I18N = True

# In template:
{% load humanize %}
{{ cedula_info.fetched_at|naturaltime }}
# Output: "hace 5 minutos"
```

### Role-Based View Decorator
```python
from functools import wraps
from django.http import HttpResponseForbidden

def leader_or_self_required(view_func):
    """Allow if user is viewing own data or is a LEADER viewing referral."""
    @wraps(view_func)
    def _wrapped_view(request, user_id=None, *args, **kwargs):
        from .models import CustomUser

        # Self-access always allowed
        if user_id is None or user_id == request.user.id:
            return view_func(request, user_id, *args, **kwargs)

        # Leader accessing referral
        if request.user.role == CustomUser.Role.LEADER:
            target_user = CustomUser.objects.filter(id=user_id).first()
            if target_user and target_user.referred_by == request.user:
                return view_func(request, user_id, *args, **kwargs)

        return HttpResponseForbidden("No tienes permiso para esta accion.")
    return _wrapped_view
```

### Triggering Toast via HX-Trigger Header
```python
# Source: django-htmx documentation
from django.http import HttpResponse

def refresh_cedula_view(request, user_id):
    # ... trigger task ...

    response = render(request, 'partials/_census_section.html', context)
    # Trigger toast on client
    response['HX-Trigger'] = '{"showToast": {"message": "Actualizacion en progreso"}}'
    return response
```

```javascript
// In template JS
document.body.addEventListener('showToast', function(evt) {
    const toastEl = document.getElementById('toast');
    const toastBody = toastEl.querySelector('.toast-body');
    toastBody.textContent = evt.detail.message;
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
});
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| jQuery AJAX polling | HTMX declarative polling | 2020 (HTMX 1.0) | No JS needed for common patterns |
| Django messages only | HX-Trigger headers | HTMX 1.3 | Real-time toast without redirect |
| Full page refresh | Partial swap | Always available | Better UX, less data transfer |

**Deprecated/outdated:**
- `hx-trigger="poll"` (old syntax, use `every Xs` instead)
- Setting HTMX via npm for simple projects (CDN is simpler)

## Open Questions

Things that couldn't be fully resolved:

1. **Exact Spanish translations for naturaltime**
   - What we know: Django's humanize respects LANGUAGE_CODE
   - What's unclear: Exact output strings (need to test with `es` locale)
   - Recommendation: Test with `LANGUAGE_CODE = 'es'`, may need custom filter if default not satisfactory

2. **HTMX 2.0 SRI hash stability**
   - What we know: Current hash provided by unpkg
   - What's unclear: If CDN versions change the hash
   - Recommendation: Use exact version URL to lock hash

## Sources

### Primary (HIGH confidence)
- [HTMX hx-trigger documentation](https://htmx.org/attributes/hx-trigger/) - Polling syntax, conditions
- [HTMX hx-disabled-elt documentation](https://htmx.org/attributes/hx-disabled-elt/) - Button disable pattern
- [Bootstrap 5.3 Spinners](https://getbootstrap.com/docs/5.3/components/spinners/) - Loading animations
- [django-htmx HTTP tools](https://django-htmx.readthedocs.io/en/latest/http.html) - HttpResponseStopPolling, trigger_client_event

### Secondary (MEDIUM confidence)
- [Django RBAC patterns](https://www.horilla.com/blogs/how-to-implement-a-role-based-access-control-rbac-system-in-django/) - Role decorator pattern
- [HTMX HX-Trigger headers](https://htmx.org/headers/hx-trigger/) - Toast notification pattern
- [django-htmx installation](https://django-htmx.readthedocs.io/en/latest/installation.html) - Optional middleware setup

### Tertiary (LOW confidence)
- WebSearch results for "Django timesince Spanish localization" - May need custom testing

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - HTMX is well-documented, Bootstrap already in project
- Architecture: HIGH - Patterns verified against official HTMX docs
- Pitfalls: MEDIUM - Some based on common issues, not project-specific testing

**Research date:** 2026-01-21
**Valid until:** 2026-03-21 (60 days - stable stack, slow-moving ecosystem)
