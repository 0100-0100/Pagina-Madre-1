# Phase 10: Referidos Page - Research

**Researched:** 2026-01-19
**Domain:** Django View + Bootstrap Table Display
**Confidence:** HIGH

## Summary

Phase 10 implements a simple read-only table page showing users referred by the current user. The requirements are straightforward: display a table with four columns (Nombre, Cedula, Telefono, Fecha de registro) and show a friendly empty state when no referrals exist.

The implementation leverages existing patterns in the codebase: Django's `@login_required` decorator, template inheritance from `base.html`, Bootstrap 5.3 tables, and the `related_name='referrals'` reverse lookup already defined on the `referred_by` field.

**Primary recommendation:** Create a simple function-based view that queries `request.user.referrals.all()`, passes the queryset to a new `referidos.html` template, and uses Bootstrap's `table table-striped table-hover` classes with responsive wrapper.

## Standard Stack

The existing project stack covers everything needed:

### Core (Already in Project)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Django | 4.2 LTS | Web framework | Project foundation |
| Bootstrap | 5.3.8 | CSS framework | Already loaded via CDN in base.html |
| Bootstrap Icons | 1.13.1 | Icon library | Already loaded via CDN in base.html |

### Supporting
No additional libraries needed. Django's built-in template system and ORM provide all required functionality.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Function-based view | Class-based ListView | Overkill for single simple view |
| Django templates | External frontend | Unnecessary complexity |
| Server-side table | DataTables.js | Out of scope per requirements |

**Installation:**
```bash
# No new dependencies required
```

## Architecture Patterns

### Recommended Project Structure
The phase adds two files to existing structure:
```
___/
├── accounts/
│   └── views.py          # Add referidos_view function
├── templates/
│   └── referidos.html    # New template (copy navbar pattern from profile.html)
```

### Pattern 1: Simple View with Queryset
**What:** Function-based view passing queryset to template
**When to use:** Read-only display of related objects
**Example:**
```python
# Source: Existing codebase pattern (views.py lines 39-53)
@login_required
def referidos_view(request):
    """View listing all users referred by the current user."""
    referrals = request.user.referrals.all().order_by('-date_joined')
    return render(request, 'referidos.html', {
        'referrals': referrals,
    })
```

### Pattern 2: Empty State Check in Template
**What:** Django template `{% if %}` with `{% empty %}` for loop
**When to use:** Lists that may be empty
**Example:**
```html
<!-- Source: Django template documentation -->
{% for referral in referrals %}
    <tr>...</tr>
{% empty %}
    <!-- Empty state shown when no referrals -->
{% endfor %}
```

### Pattern 3: Navbar Consistency
**What:** Copy navbar block from existing templates
**When to use:** All authenticated pages
**Source:** Current home.html and profile.html use identical navbar with "Referidos" link set to `href="{% url 'referidos' %}"`

### Anti-Patterns to Avoid
- **Custom pagination:** Not requested, would add unnecessary complexity
- **AJAX/dynamic loading:** Requirements call for simple table, no dynamic features
- **Table sorting/filtering:** Explicitly out of scope in REQUIREMENTS.md

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Date formatting | Custom Python formatting | Django `|date:"d/m/Y"` filter | Built-in, locale-aware |
| Empty list handling | Manual if-check around loop | `{% empty %}` tag in `{% for %}` | Cleaner, idiomatic Django |
| Responsive table | Custom CSS breakpoints | `.table-responsive` wrapper div | Bootstrap handles all breakpoints |
| Striped rows | Alternating CSS classes | `.table-striped` class | Single class, automatic |

**Key insight:** Bootstrap 5 and Django templates provide all the building blocks needed. The entire feature is simple wiring.

## Common Pitfalls

### Pitfall 1: Missing login_required
**What goes wrong:** Unauthenticated users can access `/referidos/` and trigger errors when accessing `request.user.referrals`
**Why it happens:** Copying code without decorator
**How to avoid:** Always use `@login_required` decorator on views accessing user data
**Warning signs:** Anonymous user errors in logs

### Pitfall 2: N+1 Query (Not Applicable Here)
**What goes wrong:** Accessing related objects in loop triggers separate query per row
**Why it happens:** Django lazy loading
**How to avoid:** Not applicable - we're accessing fields on the referral users themselves, not nested relationships
**Note:** `request.user.referrals.all()` returns CustomUser objects directly, no select_related needed

### Pitfall 3: Forgetting to Update URLs
**What goes wrong:** Route already exists pointing to `placeholder_view`, must update not add
**Why it happens:** Assuming new route needed
**How to avoid:** Modify existing `path('referidos/', placeholder_view, name='referidos')` to use new view
**Warning signs:** Import error or wrong view served

### Pitfall 4: Empty Table vs Empty State
**What goes wrong:** Showing empty `<table>` with headers but no rows looks broken
**Why it happens:** Putting `{% empty %}` inside `<tbody>` but still rendering `<table>` and `<thead>`
**How to avoid:** Use `{% if referrals %}` around entire table, show card/alert in else branch
**Warning signs:** Empty table visible with just column headers

### Pitfall 5: Hardcoded Navbar
**What goes wrong:** Navbar duplicated across templates gets out of sync
**Why it happens:** Copy-paste development
**How to avoid:** For now, accept duplication (consistent with existing pattern). Future: extract to include
**Note:** Nice-to-have, not required for this phase

## Code Examples

Verified patterns from the existing codebase and official documentation:

### View Function
```python
# Pattern from accounts/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def referidos_view(request):
    """View listing all users referred by the current user."""
    referrals = request.user.referrals.all().order_by('-date_joined')
    return render(request, 'referidos.html', {
        'referrals': referrals,
    })
```

### URL Update
```python
# In accounts/urls.py - change placeholder_view to referidos_view
from .views import referidos_view  # Add to imports

path('referidos/', referidos_view, name='referidos'),  # Replace placeholder_view
```

### Bootstrap Table Structure
```html
<!-- Source: Bootstrap 5.3 documentation - tables -->
{% if referrals %}
<div class="table-responsive">
    <table class="table table-striped table-hover">
        <thead class="table-light">
            <tr>
                <th scope="col">Nombre</th>
                <th scope="col">Cedula</th>
                <th scope="col">Telefono</th>
                <th scope="col">Fecha de registro</th>
            </tr>
        </thead>
        <tbody>
            {% for referral in referrals %}
            <tr>
                <td>{{ referral.nombre_completo }}</td>
                <td>{{ referral.cedula }}</td>
                <td>{{ referral.phone }}</td>
                <td>{{ referral.date_joined|date:"d/m/Y" }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<!-- Empty state -->
{% endif %}
```

### Empty State Pattern
```html
<!-- Pattern consistent with existing Bootstrap card usage in project -->
<div class="card shadow">
    <div class="card-body text-center p-5">
        <i class="bi bi-people text-muted" style="font-size: 3rem;"></i>
        <h5 class="mt-3">Aun no tienes referidos</h5>
        <p class="text-muted mb-3">Comparte tu enlace de referido para empezar</p>
        <a href="{% url 'home' %}" class="btn btn-primary">
            <i class="bi bi-house"></i> Ir al inicio
        </a>
    </div>
</div>
```

### Date Formatting
```html
<!-- Django date filter - d/m/Y gives day/month/year format -->
{{ referral.date_joined|date:"d/m/Y" }}
<!-- Example output: 19/01/2026 -->
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Django 3.x templates | Django 4.2 LTS templates | 2023 | No change needed |
| Bootstrap 4 tables | Bootstrap 5.3 tables | 2021 | Class names identical |

**Deprecated/outdated:**
- None relevant to this phase

## Open Questions

None. The phase requirements are fully covered by existing patterns.

## Sources

### Primary (HIGH confidence)
- Existing codebase: `accounts/models.py` - CustomUser model with `referrals` related_name
- Existing codebase: `accounts/views.py` - Pattern for `@login_required` views
- Existing codebase: `templates/home.html`, `templates/profile.html` - Navbar and card patterns
- Bootstrap 5.3 official docs: https://getbootstrap.com/docs/5.3/content/tables/

### Secondary (MEDIUM confidence)
- Django 4.2 template date filter documentation (stable, unchanged API)

### Tertiary (LOW confidence)
- None required

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using existing project dependencies only
- Architecture: HIGH - Patterns copied from existing codebase
- Pitfalls: HIGH - Based on direct code inspection

**Research date:** 2026-01-19
**Valid until:** No expiration - patterns are stable, no external dependencies
