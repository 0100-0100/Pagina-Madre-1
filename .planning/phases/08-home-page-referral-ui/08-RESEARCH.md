# Phase 8: Home Page Referral UI - Research

**Researched:** 2026-01-19
**Domain:** Bootstrap 5 Components, JavaScript Clipboard API, Django Template Context
**Confidence:** HIGH

## Summary

This phase enhances the existing home page to display referral statistics, provide a copy-to-clipboard button for the referral link, and add navigation links to upcoming Perfil and Referidos pages. The implementation uses Bootstrap 5.3 components (progress bar, toast, cards) already available via the existing CDN setup, adds Bootstrap Icons via CDN for visual elements, and leverages the modern Clipboard API for copy functionality.

The home view needs modification to pass referral count and referral URL to the template context. The template updates are substantial but straightforward: add Bootstrap Icons CSS to base.html, update the navbar with new navigation links, and replace the current card content with two stacked cards (stats and share). All JavaScript for copy-to-clipboard and toast notifications uses vanilla JS with Bootstrap's JavaScript bundle already included.

**Primary recommendation:** Use Bootstrap 5.3's built-in progress bar and toast components with the modern `navigator.clipboard.writeText()` API. Add Bootstrap Icons 1.13.1 via jsDelivr CDN to match the existing Bootstrap setup.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Bootstrap | 5.3.8 | UI components (progress, toast, cards) | Already in project via CDN |
| Bootstrap Icons | 1.13.1 | Icon font for UI elements | Official companion to Bootstrap |
| Clipboard API | (browser built-in) | Copy text to clipboard | Modern standard, no polyfill needed |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Django Template Engine | 4.2 | Template rendering, URL building | Pass context data, build absolute URLs |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Bootstrap Icons | Font Awesome | Font Awesome requires separate CDN, Bootstrap Icons matches existing stack |
| navigator.clipboard | execCommand('copy') | execCommand is deprecated, Clipboard API is modern standard |
| Bootstrap Toast | Custom notification | Toast is built-in, styled consistently with Bootstrap |

**Installation:**
```html
<!-- Add to base.html <head> after Bootstrap CSS -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css"
      rel="stylesheet"
      integrity="sha384-CK2SzKma4jA5H/MXDUU7i1TqZlCFaD4T01vtyDFvPlD97JQyS+IsSh1nI2EFbpyk"
      crossorigin="anonymous">
```

## Architecture Patterns

### Recommended Project Structure
```
___/
├── accounts/
│   └── views.py           # Modify home() to pass referral context
└── templates/
    ├── base.html          # Add Bootstrap Icons CDN
    └── home.html          # Update navbar + add stats/share cards
```

### Pattern 1: Bootstrap 5 Progress Bar
**What:** Visual progress indicator showing referral count toward goal.
**When to use:** When displaying numeric progress as a percentage.
**Example:**
```html
<!-- Source: https://getbootstrap.com/docs/5.3/components/progress/ -->
<div class="progress" role="progressbar"
     aria-label="Progreso de referidos"
     aria-valuenow="{{ referral_count }}"
     aria-valuemin="0"
     aria-valuemax="{{ user.referral_goal }}">
    <div class="progress-bar" style="width: {{ progress_percent }}%"></div>
</div>
<p class="text-muted mt-2">{{ referral_count }} de {{ user.referral_goal }} referidos</p>
```

**Key points:**
- Progress bar wrapper has `role="progressbar"` for accessibility
- `aria-valuenow`, `aria-valuemin`, `aria-valuemax` required for screen readers
- Width is set via inline `style` or Bootstrap width utilities (w-25, w-50, etc.)
- Calculate percentage in view: `min(100, (count / goal) * 100)`

### Pattern 2: Bootstrap 5 Toast for Copy Feedback
**What:** Non-intrusive notification that appears briefly to confirm an action.
**When to use:** After clipboard copy, to confirm success without disrupting flow.
**Example:**
```html
<!-- Source: https://getbootstrap.com/docs/5.3/components/toasts/ -->
<!-- Toast container positioned top-right -->
<div class="toast-container position-fixed top-0 end-0 p-3">
    <div id="copyToast" class="toast align-items-center text-bg-success"
         role="status" aria-live="polite" aria-atomic="true">
        <div class="d-flex">
            <div class="toast-body">
                Enlace copiado al portapapeles
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto"
                    data-bs-dismiss="toast" aria-label="Cerrar"></button>
        </div>
    </div>
</div>
```

**JavaScript to show toast:**
```javascript
// Source: Bootstrap 5.3 Toast JavaScript API
const toastEl = document.getElementById('copyToast');
const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
toast.show();
```

### Pattern 3: Clipboard API for Copy-to-Clipboard
**What:** Modern browser API for writing text to clipboard.
**When to use:** When users need to copy text (URLs, codes) without selecting it.
**Example:**
```javascript
// Source: https://developer.mozilla.org/en-US/docs/Web/API/Clipboard/writeText
async function copyReferralLink() {
    const url = document.getElementById('referralUrl').value;
    try {
        await navigator.clipboard.writeText(url);
        // Show success feedback
    } catch (err) {
        console.error('Failed to copy:', err);
        // Show error feedback
    }
}
```

**Key points:**
- Returns a Promise - use async/await or .then()/.catch()
- Requires HTTPS or localhost (secure context)
- No permission prompt on user gesture (button click)
- Throws `NotAllowedError` if clipboard access denied

### Pattern 4: Building Absolute URL in Django View
**What:** Generate full URL (with scheme and domain) for referral link.
**When to use:** When the URL needs to be shared externally (copy to clipboard, social).
**Example:**
```python
# Source: Django HttpRequest.build_absolute_uri()
from django.urls import reverse

def home(request):
    referral_url = request.build_absolute_uri(
        reverse('register') + f'?ref={request.user.referral_code}'
    )
    return render(request, 'home.html', {'referral_url': referral_url})
```

**Key points:**
- `build_absolute_uri()` uses request scheme and host
- Works correctly behind proxies with proper ALLOWED_HOSTS config
- Combine with `reverse()` for URL name resolution

### Pattern 5: Navbar Navigation Links with Icons
**What:** Navigation items with Bootstrap Icons and text labels.
**When to use:** When adding persistent navigation across the app.
**Example:**
```html
<!-- Source: Bootstrap 5 navbar patterns + Bootstrap Icons -->
<ul class="navbar-nav ms-auto align-items-center">
    <li class="nav-item">
        <a class="nav-link" href="{% url 'perfil' %}">
            <i class="bi bi-person"></i> Perfil
        </a>
    </li>
    <li class="nav-item">
        <a class="nav-link" href="{% url 'referidos' %}">
            <i class="bi bi-people"></i> Referidos
        </a>
    </li>
    <!-- Logout button... -->
</ul>
```

### Anti-Patterns to Avoid
- **execCommand('copy'):** Deprecated, use Clipboard API instead.
- **Inline onclick handlers:** Use addEventListener for maintainability.
- **Hardcoded URLs:** Always use `{% url %}` tag and `reverse()`.
- **Missing aria attributes:** Progress bars need aria-valuenow/min/max.
- **Toast without position-fixed container:** Toast won't stay visible during scroll.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Progress indicator | Custom div with width calc | Bootstrap progress bar | Handles accessibility, styling, animations |
| Notification popup | Custom modal/alert | Bootstrap toast | Non-blocking, auto-dismiss, consistent styling |
| Copy to clipboard | execCommand or custom solution | navigator.clipboard.writeText() | Modern API, Promise-based, handles permissions |
| Icon fonts | Custom SVGs or images | Bootstrap Icons | CDN-ready, consistent with Bootstrap |
| Absolute URL building | String concatenation | request.build_absolute_uri() | Handles scheme, port, proxy headers |

**Key insight:** Bootstrap 5.3 includes all UI components needed for this phase. The only addition is Bootstrap Icons CSS via CDN.

## Common Pitfalls

### Pitfall 1: Clipboard API Fails on HTTP
**What goes wrong:** `navigator.clipboard` is undefined or throws SecurityError.
**Why it happens:** Clipboard API requires secure context (HTTPS or localhost).
**How to avoid:** In development, use localhost (not IP address). In production, use HTTPS.
**Warning signs:** TypeError on clipboard.writeText, works locally but fails on staging.

### Pitfall 2: Toast Not Showing
**What goes wrong:** Toast element exists but `toast.show()` does nothing.
**Why it happens:** Bootstrap JS not loaded, or toast initialized incorrectly.
**How to avoid:**
- Ensure bootstrap.bundle.min.js is loaded (already in base.html)
- Use `bootstrap.Toast.getOrCreateInstance()` for reliability
- Check toast container has `position-fixed`
**Warning signs:** No console errors but toast never appears.

### Pitfall 3: Progress Bar Shows Wrong Width
**What goes wrong:** Progress bar doesn't reflect actual progress percentage.
**Why it happens:** Missing style attribute or incorrect percentage calculation.
**How to avoid:**
- Calculate in view: `progress_percent = min(100, int((count / goal) * 100))`
- Handle division by zero when goal is 0
- Use inline style: `style="width: {{ progress_percent }}%"`
**Warning signs:** Bar always empty or always full.

### Pitfall 4: Navbar Links 404 Before Pages Exist
**What goes wrong:** Clicking Perfil/Referidos links causes 404 error.
**Why it happens:** URL routes not yet defined (future phases).
**How to avoid:**
- Define placeholder URL routes immediately that return 404 or redirect
- Or use `href="#"` with `onclick="alert('Coming soon')"` temporarily
- Recommendation: Add routes with placeholder views in this phase
**Warning signs:** NoReverseMatch error if using `{% url %}` without route.

### Pitfall 5: Button State Not Resetting
**What goes wrong:** Copy button stays stuck on "Copiado!" text.
**Why it happens:** Timeout not set correctly, or error prevents reset.
**How to avoid:**
```javascript
button.textContent = 'Copiado!';
setTimeout(() => {
    button.innerHTML = '<i class="bi bi-clipboard"></i> Copiar Link de Referido';
}, 2000);
```
**Warning signs:** Button text changes once and never reverts.

### Pitfall 6: referral_count Query N+1
**What goes wrong:** Counting referrals becomes slow with many users.
**Why it happens:** Using `user.referrals.count()` in template without annotation.
**How to avoid:** Count in view, pass as context:
```python
referral_count = request.user.referrals.count()
```
**Warning signs:** Slow page load, database query per page view.

## Code Examples

Verified patterns from official sources:

### Updated Home View with Referral Context
```python
# Source: Django patterns
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse

@login_required
def home(request):
    """Home page view with referral statistics."""
    user = request.user
    referral_count = user.referrals.count()
    referral_goal = user.referral_goal

    # Calculate progress percentage (handle zero goal)
    if referral_goal > 0:
        progress_percent = min(100, int((referral_count / referral_goal) * 100))
    else:
        progress_percent = 100  # Goal of 0 means always complete

    # Build absolute referral URL
    referral_url = request.build_absolute_uri(
        reverse('register') + f'?ref={user.referral_code}'
    )

    context = {
        'user': user,
        'referral_count': referral_count,
        'referral_goal': referral_goal,
        'progress_percent': progress_percent,
        'referral_url': referral_url,
    }
    return render(request, 'home.html', context)
```

### Bootstrap Icons CDN Addition to base.html
```html
<!-- Add after Bootstrap CSS in <head> -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css"
      rel="stylesheet"
      integrity="sha384-CK2SzKma4jA5H/MXDUU7i1TqZlCFaD4T01vtyDFvPlD97JQyS+IsSh1nI2EFbpyk"
      crossorigin="anonymous">
```

### Stats Card with Progress Bar
```html
<!-- Stats Card -->
<div class="card shadow mb-4">
    <div class="card-body text-center p-4">
        <h1 class="display-4 fw-bold text-primary mb-1">{{ referral_count }}</h1>
        <p class="text-muted mb-3">referidos</p>

        <div class="progress mb-2" role="progressbar"
             aria-label="Progreso de referidos"
             aria-valuenow="{{ referral_count }}"
             aria-valuemin="0"
             aria-valuemax="{{ referral_goal }}">
            <div class="progress-bar" style="width: {{ progress_percent }}%"></div>
        </div>

        <p class="text-muted small mb-0">{{ referral_count }} de {{ referral_goal }} referidos</p>

        {% if referral_count == 0 %}
        <p class="text-success mt-3 mb-0">
            <i class="bi bi-gift"></i> Comparte tu enlace!
        </p>
        {% endif %}
    </div>
</div>
```

### Share Card with Copy Button
```html
<!-- Share Card -->
<div class="card shadow">
    <div class="card-body text-center p-4">
        <!-- Hidden input holds the URL -->
        <input type="hidden" id="referralUrl" value="{{ referral_url }}">

        <button type="button" class="btn btn-primary btn-lg" id="copyBtn">
            <i class="bi bi-clipboard"></i> Copiar Link de Referido
        </button>
    </div>
</div>

<!-- Toast container -->
<div class="toast-container position-fixed top-0 end-0 p-3">
    <div id="copyToast" class="toast align-items-center text-bg-success"
         role="status" aria-live="polite" aria-atomic="true">
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi bi-check-circle"></i> Enlace copiado al portapapeles
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto"
                    data-bs-dismiss="toast" aria-label="Cerrar"></button>
        </div>
    </div>
</div>
```

### Copy-to-Clipboard JavaScript
```javascript
// Source: MDN Clipboard API + Bootstrap Toast API
(function() {
    'use strict';

    const copyBtn = document.getElementById('copyBtn');
    const referralUrl = document.getElementById('referralUrl');
    const toastEl = document.getElementById('copyToast');

    if (copyBtn && referralUrl && toastEl) {
        const toast = new bootstrap.Toast(toastEl, { delay: 3000 });

        copyBtn.addEventListener('click', async function() {
            try {
                await navigator.clipboard.writeText(referralUrl.value);

                // Update button text temporarily
                const originalHTML = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="bi bi-check-lg"></i> Copiado!';
                copyBtn.classList.remove('btn-primary');
                copyBtn.classList.add('btn-success');

                // Show toast
                toast.show();

                // Reset button after 2 seconds
                setTimeout(() => {
                    copyBtn.innerHTML = originalHTML;
                    copyBtn.classList.remove('btn-success');
                    copyBtn.classList.add('btn-primary');
                }, 2000);

            } catch (err) {
                console.error('Copy failed:', err);
                // Fallback: show URL in alert
                alert('No se pudo copiar. Tu enlace es: ' + referralUrl.value);
            }
        });
    }
})();
```

### Updated Navbar with Navigation Links
```html
<ul class="navbar-nav ms-auto align-items-center">
    <li class="nav-item">
        <a class="nav-link" href="{% url 'perfil' %}">
            <i class="bi bi-person"></i> Perfil
        </a>
    </li>
    <li class="nav-item">
        <a class="nav-link" href="{% url 'referidos' %}">
            <i class="bi bi-people"></i> Referidos
        </a>
    </li>
    <li class="nav-item">
        <form method="post" action="{% url 'logout' %}" class="d-inline">
            {% csrf_token %}
            <button type="submit" class="btn btn-outline-light btn-sm ms-2">
                <i class="bi bi-box-arrow-right"></i> Cerrar Sesion
            </button>
        </form>
    </li>
</ul>
```

### Placeholder URL Routes (to avoid NoReverseMatch)
```python
# accounts/urls.py
from django.urls import path
from django.http import HttpResponse

def placeholder_view(request):
    """Temporary placeholder for future pages."""
    return HttpResponse("Coming soon", status=200)

urlpatterns = [
    # ... existing routes ...
    path('perfil/', placeholder_view, name='perfil'),
    path('referidos/', placeholder_view, name='referidos'),
]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| document.execCommand('copy') | navigator.clipboard.writeText() | 2020+ | Async, Promise-based, more reliable |
| jQuery $.ajax | Vanilla JS fetch/async-await | 2015+ | No jQuery dependency |
| Bootstrap 4 progress | Bootstrap 5 progress (wrapper-based) | 2021 | Different HTML structure |
| Font Awesome | Bootstrap Icons | 2021+ | Matches Bootstrap ecosystem |

**Deprecated/outdated:**
- `document.execCommand('copy')` - deprecated, use Clipboard API
- Bootstrap 4 progress structure (inner-only) - Bootstrap 5 requires wrapper
- jQuery for DOM manipulation - vanilla JS preferred for simple operations

## Open Questions

Things that couldn't be fully resolved:

1. **Toast Auto-Dismiss Timing**
   - What we know: Bootstrap default is 5000ms, user decision was "toast notification"
   - What's unclear: Exact preferred duration not specified in CONTEXT.md
   - Recommendation: Use 3000ms (3 seconds) - enough to read, not intrusive

2. **Navigation Links Before Routes Exist**
   - What we know: Perfil and Referidos pages are future phases
   - What's unclear: Should routes exist now (placeholder) or handle NoReverseMatch?
   - Recommendation: Add placeholder routes now to avoid template errors

3. **Mobile Responsiveness of Two-Card Layout**
   - What we know: Cards should be "centered, medium width (50-60%)"
   - What's unclear: Exact behavior on mobile screens
   - Recommendation: Use `col-lg-6 col-md-8 col-12` for responsive centering

## Sources

### Primary (HIGH confidence)
- [Bootstrap 5.3 Progress Documentation](https://getbootstrap.com/docs/5.3/components/progress/) - Progress bar structure, accessibility
- [Bootstrap 5.3 Toasts Documentation](https://getbootstrap.com/docs/5.3/components/toasts/) - Toast markup, JavaScript API, positioning
- [Bootstrap Icons](https://icons.getbootstrap.com/) - Icon usage pattern, CDN setup
- [MDN Clipboard API](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard/writeText) - writeText usage, security requirements
- [Django HttpRequest.build_absolute_uri()](https://docs.djangoproject.com/en/4.2/ref/request-response/#django.http.HttpRequest.build_absolute_uri) - Absolute URL generation

### Secondary (MEDIUM confidence)
- [jsDelivr Bootstrap Icons CDN](https://www.jsdelivr.com/package/npm/bootstrap-icons) - CDN URL, version info
- Generated SRI hash for Bootstrap Icons 1.13.1 - Computed via openssl

### Tertiary (LOW confidence)
- None - all findings verified with official sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using existing Bootstrap + documented CDN addition
- Architecture: HIGH - Following established project patterns from login/register templates
- Pitfalls: HIGH - Based on official documentation and known browser behaviors

**Research date:** 2026-01-19
**Valid until:** 2026-04-19 (Bootstrap 5.3 stable, Clipboard API mature)
