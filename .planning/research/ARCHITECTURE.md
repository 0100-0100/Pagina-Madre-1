# Architecture Patterns: Django Templates with Bootstrap 5

**Project:** Pagina Madre
**Domain:** Django web application with Bootstrap 5 UI
**Researched:** 2026-01-19
**Confidence:** HIGH

## Executive Summary

Django's template inheritance system provides a powerful pattern for integrating Bootstrap 5 with DRY principles. The recommended architecture uses a three-level template hierarchy: base template (site-wide), section templates (optional), and page templates. Bootstrap CSS/JS is included once in the base template, and child templates extend it using named blocks for content, extra CSS, and extra JavaScript.

**Key findings:**
- Project-level templates directory recommended over app-level for centralized management
- Base template defines 6-8 core blocks for maximum flexibility
- Bootstrap grid (container/row/col) lives in page templates, not base template
- Block naming follows community conventions: `title`, `extra_css`, `content`, `extra_js`, `navbar`

---

## Recommended Architecture

### Template Hierarchy

```
templates/
├── base.html                    # Site-wide base (Bootstrap includes, navbar)
├── home.html                    # Extends base.html
└── registration/
    ├── login.html               # Extends base.html
    └── register.html            # Extends base.html
```

**Three-level pattern (for larger projects):**
```
templates/
├── base.html                    # Level 1: Site-wide (Bootstrap, navbar, footer)
├── base_auth.html              # Level 2: Auth section (extends base.html)
├── base_dashboard.html         # Level 2: Dashboard section (extends base.html)
├── registration/
│   ├── login.html              # Level 3: Specific page (extends base_auth.html)
│   └── register.html
└── dashboard/
    └── home.html               # Level 3: Specific page (extends base_dashboard.html)
```

**Current project status:**
- 3 templates: `home.html`, `registration/login.html`, `registration/register.html`
- All currently standalone (no inheritance)
- Located in `___/templates/` and `___/templates/registration/`

---

## Base Template Pattern

### Core Structure (base.html)

```django
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Pagina Madre{% endblock %}</title>

    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
          rel="stylesheet"
          integrity="sha384-9ndCyUaIbzAi2FUVXJi0CjmCapSmO7SnpJef0486qhLnuZ2cdeRhO02iuK6FUUVM"
          crossorigin="anonymous">

    {% block extra_css %}{% endblock %}
</head>
<body>
    {% block navbar %}
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container-fluid">
            <a class="navbar-brand" href="{% url 'home' %}">Pagina Madre</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                    data-bs-target="#navbarNav" aria-controls="navbarNav"
                    aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    {% if user.is_authenticated %}
                        <li class="nav-item">
                            <span class="navbar-text me-2">{{ user.nombre_completo|default:user.username }}</span>
                        </li>
                        <li class="nav-item">
                            <form method="post" action="{% url 'logout' %}" class="d-inline">
                                {% csrf_token %}
                                <button type="submit" class="btn btn-link nav-link">Logout</button>
                            </form>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'login' %}">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'register' %}">Register</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
    {% endblock %}

    {% block messages %}
    {% if messages %}
        <div class="container mt-3">
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            {% endfor %}
        </div>
    {% endif %}
    {% endblock %}

    {% block content %}
    <!-- Child templates override this -->
    {% endblock %}

    {% block footer %}
    <footer class="mt-5 py-3 bg-light">
        <div class="container text-center">
            <p class="text-muted mb-0">&copy; 2026 Pagina Madre</p>
        </div>
    </footer>
    {% endblock %}

    <!-- Bootstrap 5 JS Bundle (includes Popper) -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
            integrity="sha384-geWF76RCwLtnZ8qwWowPQNguL3RmwHVBC9FhGdlKrxdiJJigb/j/68SIy3Te4Bkz"
            crossorigin="anonymous"></script>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Block Definitions

| Block Name | Location | Purpose | Default Content | Override Pattern |
|------------|----------|---------|-----------------|------------------|
| `title` | `<head>` | Page title in browser tab | "Pagina Madre" | Complete override |
| `extra_css` | `<head>`, after Bootstrap CSS | Page-specific stylesheets | None | Additive |
| `navbar` | Top of `<body>` | Site navigation | Bootstrap navbar | Complete override (rarely) |
| `messages` | After navbar | Django messages/alerts | Bootstrap alerts | Complete override (rarely) |
| `content` | Main body | Page-specific content | None | Complete override (always) |
| `footer` | Bottom of `<body>` | Site footer | Copyright notice | Complete override |
| `extra_js` | Before `</body>`, after Bootstrap JS | Page-specific JavaScript | None | Additive |

**Why this block structure:**
- **`extra_css`**: Placed after Bootstrap CSS so custom styles can override Bootstrap defaults
- **`extra_js`**: Placed after Bootstrap JS so page scripts can use Bootstrap components (modals, tooltips, etc.)
- **`navbar` and `footer`**: Separate blocks for flexibility but rarely overridden (use `{{ block.super }}` to extend)
- **`content`**: Always overridden, no default content

---

## Child Template Patterns

### Pattern 1: Simple Content Page

**Use case:** Page with simple content, no custom CSS/JS

```django
{% extends "base.html" %}

{% block title %}Home - Pagina Madre{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <h1>Bienvenido</h1>
            <p class="lead">Hola, {{ user.nombre_completo|default:user.username }}</p>
        </div>
    </div>
</div>
{% endblock %}
```

**Key points:**
- Bootstrap grid (`container > row > col-*`) goes in the `content` block, NOT in base.html
- This gives each page control over its layout (full-width, centered, multi-column, etc.)

### Pattern 2: Form Page with Custom Styles

**Use case:** Login/Register pages with centered form and custom styling

```django
{% extends "base.html" %}

{% block title %}Login - Pagina Madre{% endblock %}

{% block extra_css %}
<style>
    .auth-form {
        max-width: 400px;
        margin: 0 auto;
    }
    .auth-form .form-control {
        border-radius: 0.5rem;
    }
</style>
{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card shadow-sm auth-form">
                <div class="card-body">
                    <h1 class="card-title text-center mb-4">Login</h1>

                    {% if form.errors %}
                        <div class="alert alert-danger">
                            <p>Invalid username or password. Please try again.</p>
                        </div>
                    {% endif %}

                    <form method="post">
                        {% csrf_token %}

                        <div class="mb-3">
                            <label for="id_username" class="form-label">Cédula:</label>
                            <input type="text"
                                   name="username"
                                   id="id_username"
                                   class="form-control {% if form.username.errors %}is-invalid{% endif %}"
                                   required>
                            {% if form.username.errors %}
                                <div class="invalid-feedback">{{ form.username.errors }}</div>
                            {% endif %}
                        </div>

                        <div class="mb-3">
                            <label for="id_password" class="form-label">Password:</label>
                            <input type="password"
                                   name="password"
                                   id="id_password"
                                   class="form-control {% if form.password.errors %}is-invalid{% endif %}"
                                   required>
                            {% if form.password.errors %}
                                <div class="invalid-feedback">{{ form.password.errors }}</div>
                            {% endif %}
                        </div>

                        <div class="form-check mb-3">
                            <input type="checkbox"
                                   name="remember_me"
                                   value="1"
                                   id="remember_me"
                                   class="form-check-input">
                            <label for="remember_me" class="form-check-label">
                                Remember me (stay logged in for 14 days)
                            </label>
                        </div>

                        <button type="submit" class="btn btn-primary w-100">Login</button>
                    </form>

                    <p class="text-center mt-3 mb-0">
                        Don't have an account? <a href="{% url 'register' %}">Create account</a>
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

**Key points:**
- `extra_css` block adds page-specific styles without external file
- Bootstrap form classes: `form-label`, `form-control`, `is-invalid`, `invalid-feedback`
- Bootstrap layout classes: `card`, `shadow-sm`, `w-100`, `mb-3`

### Pattern 3: Interactive Page with JavaScript

**Use case:** Page with JavaScript for dynamic behavior

```django
{% extends "base.html" %}

{% block title %}Dashboard - Pagina Madre{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-12">
            <h1>Dashboard</h1>
            <button type="button"
                    class="btn btn-primary"
                    data-bs-toggle="modal"
                    data-bs-target="#exampleModal">
                Open Modal
            </button>
        </div>
    </div>
</div>

<!-- Bootstrap Modal -->
<div class="modal fade" id="exampleModal" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="exampleModalLabel">Example Modal</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                Modal content here.
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    // Custom JavaScript after Bootstrap is loaded
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Dashboard loaded');

        // Initialize Bootstrap tooltips/popovers if needed
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    });
</script>
{% endblock %}
```

**Key points:**
- `extra_js` block ensures JavaScript runs after Bootstrap JS is loaded
- Bootstrap components (modals, tooltips, etc.) require Bootstrap JS
- `DOMContentLoaded` ensures DOM is ready before running scripts

### Pattern 4: Extending a Block (Not Replacing)

**Use case:** Add to navbar while keeping default items

```django
{% extends "base.html" %}

{% block navbar %}
{{ block.super }}
<!-- Additional navbar content injected after default navbar -->
<div class="container-fluid bg-secondary text-white py-2">
    <div class="container">
        <small>Special announcement: New feature released!</small>
    </div>
</div>
{% endblock %}

{% block content %}
<!-- Page content -->
{% endblock %}
```

**Key points:**
- `{{ block.super }}` includes parent block content
- Allows extending/augmenting instead of replacing
- Use sparingly (usually for navbar/footer modifications)

---

## Bootstrap Grid Integration

### Grid Lives in Content Block, Not Base

**Anti-pattern (DON'T DO THIS):**
```django
<!-- base.html - WRONG -->
<div class="container">
    <div class="row">
        <div class="col-md-8">
            {% block content %}{% endblock %}
        </div>
        <div class="col-md-4">
            {% block sidebar %}{% endblock %}
        </div>
    </div>
</div>
```

**Why this is bad:**
- Forces all pages into same grid structure
- Can't have full-width pages
- Can't have pages without sidebar
- Inflexible

**Correct pattern:**
```django
<!-- base.html - CORRECT -->
{% block content %}
<!-- Child templates control their own layout -->
{% endblock %}

<!-- child-template.html -->
{% block content %}
<div class="container">
    <div class="row">
        <div class="col-md-8">
            <!-- Main content -->
        </div>
        <div class="col-md-4">
            <!-- Sidebar -->
        </div>
    </div>
</div>
{% endblock %}
```

**Why this is better:**
- Each page controls its layout
- Full-width pages: skip container, use `container-fluid`
- Centered content: use `offset-*` classes
- Different pages, different grids

### Common Grid Patterns

#### Centered Content (Login/Register)
```django
<div class="container mt-5">
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <!-- Centered content, takes 50% width on medium+ screens -->
        </div>
    </div>
</div>
```

#### Two-Column Layout (Dashboard)
```django
<div class="container mt-5">
    <div class="row">
        <div class="col-md-8">
            <!-- Main content (66% width) -->
        </div>
        <div class="col-md-4">
            <!-- Sidebar (33% width) -->
        </div>
    </div>
</div>
```

#### Full-Width Hero + Contained Content
```django
<!-- Full-width hero -->
<div class="bg-primary text-white py-5">
    <div class="container">
        <h1>Welcome</h1>
    </div>
</div>

<!-- Contained content -->
<div class="container mt-5">
    <div class="row">
        <div class="col-md-12">
            <!-- Content -->
        </div>
    </div>
</div>
```

#### Multi-Column Cards
```django
<div class="container mt-5">
    <div class="row">
        <div class="col-md-4">
            <div class="card"><!-- Card 1 --></div>
        </div>
        <div class="col-md-4">
            <div class="card"><!-- Card 2 --></div>
        </div>
        <div class="col-md-4">
            <div class="card"><!-- Card 3 --></div>
        </div>
    </div>
</div>
```

---

## File Organization

### Project-Level Templates (Recommended)

**Directory structure:**
```
project_root/
├── manage.py
├── pagina_madre/              # Project config
│   ├── settings.py
│   └── urls.py
├── ___/                       # App directory
│   ├── models.py
│   ├── views.py
│   └── urls.py
└── templates/                 # Project-level templates
    ├── base.html              # Site-wide base
    ├── home.html
    └── registration/
        ├── login.html
        └── register.html
```

**settings.py configuration:**
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Project-level templates
        'APP_DIRS': True,  # Also check app-level templates
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

**Template lookup order:**
1. Project-level: `templates/` (checked first)
2. App-level: `___/templates/` (checked if not found in project-level)

**Why project-level is recommended:**
- Centralized location (easier to find templates)
- Easier to enforce consistent base template usage
- Clearer separation between app logic and presentation
- Better for projects with multiple apps sharing templates

### App-Level Templates (Alternative)

**Directory structure:**
```
project_root/
├── manage.py
├── pagina_madre/
│   ├── settings.py
│   └── urls.py
└── ___/
    ├── models.py
    ├── views.py
    ├── urls.py
    └── templates/
        ├── base.html          # Could be duplicated across apps
        ├── ___/               # App name subdirectory (namespace)
        │   └── home.html
        └── registration/
            ├── login.html
            └── register.html
```

**When to use:**
- Reusable Django apps (distributed separately)
- Very large projects with independent app teams
- Apps that need isolated template namespaces

**Namespace pattern:**
```django
<!-- Without namespace -->
{% extends "base.html" %}  <!-- Which app's base.html? -->

<!-- With namespace -->
{% extends "___/base.html" %}  <!-- Explicitly from ___ app -->
```

### Current Project Migration Path

**Current state:**
```
___/templates/
├── home.html
└── registration/
    ├── login.html
    └── register.html
```

**Recommended migration:**
```
1. Create project-level templates/
2. Move ___/templates/ → templates/
3. Create templates/base.html
4. Update home.html, login.html, register.html to extend base.html
5. Delete ___/templates/ (now empty)
```

**Result:**
```
templates/
├── base.html              # NEW: Site-wide base
├── home.html              # MOVED + UPDATED to extend base.html
└── registration/
    ├── login.html         # MOVED + UPDATED to extend base.html
    └── register.html      # MOVED + UPDATED to extend base.html
```

---

## Template Naming Conventions

### Block Names (Community Standard)

| Block Name | Purpose | Notes |
|------------|---------|-------|
| `title` | Page title in `<title>` tag | Always override |
| `extra_css` | Additional CSS after framework CSS | Additive |
| `extra_head` | Additional `<head>` content (meta tags, etc.) | Additive |
| `navbar` | Navigation bar | Rarely override |
| `messages` | Django messages/alerts | Rarely override |
| `content` | Main page content | Always override |
| `sidebar` | Sidebar content (if base has sidebar) | Optional override |
| `footer` | Site footer | Rarely override |
| `extra_js` | Additional JS after framework JS | Additive |

**Naming conventions:**
- Use `extra_*` for additive blocks (CSS, JS, head content)
- Use descriptive nouns for content areas (`navbar`, `content`, `footer`)
- Use `block.super` when extending instead of replacing

### Template File Names

| Pattern | Example | Use Case |
|---------|---------|----------|
| `base.html` | `base.html` | Site-wide base template |
| `base_SECTION.html` | `base_auth.html` | Section-specific base |
| `OBJECT_list.html` | `user_list.html` | List view (Django convention) |
| `OBJECT_detail.html` | `user_detail.html` | Detail view (Django convention) |
| `OBJECT_form.html` | `user_form.html` | Create/Update form (Django convention) |
| `OBJECT_confirm_delete.html` | `user_confirm_delete.html` | Delete confirmation (Django convention) |
| `ACTION.html` | `login.html`, `register.html` | Action-specific pages |
| `PAGE.html` | `home.html`, `about.html` | Simple content pages |

**Why follow Django conventions:**
- Generic views automatically look for these names
- Easier for other Django developers to understand
- Consistent with Django ecosystem

### Layout Templates (Advanced)

For complex projects with multiple layouts:

```
templates/
├── base.html                  # Site-wide base
├── layouts/
│   ├── single_column.html     # Extends base.html
│   ├── two_column.html        # Extends base.html
│   └── three_column.html      # Extends base.html
└── pages/
    └── about.html             # Extends layouts/single_column.html
```

**Layout template example:**
```django
<!-- layouts/two_column.html -->
{% extends "base.html" %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-8">
            {% block main_column %}{% endblock %}
        </div>
        <div class="col-md-4">
            {% block sidebar_column %}{% endblock %}
        </div>
    </div>
</div>
{% endblock %}
```

**Page using layout:**
```django
<!-- pages/blog_post.html -->
{% extends "layouts/two_column.html" %}

{% block main_column %}
    <h1>{{ post.title }}</h1>
    <p>{{ post.content }}</p>
{% endblock %}

{% block sidebar_column %}
    <h3>Related Posts</h3>
    <!-- Sidebar content -->
{% endblock %}
```

**When to use layout templates:**
- Multiple distinct layouts in the same project
- Frequently reused column structures
- Complex grid patterns

**When NOT to use:**
- Simple projects (like current Pagina Madre)
- When most pages have unique layouts
- Adds unnecessary complexity for 3-5 templates

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Repeating Bootstrap Includes

**What goes wrong:**
```django
<!-- login.html - BAD -->
<!DOCTYPE html>
<html>
<head>
    <link href="bootstrap.css" rel="stylesheet">  <!-- Repeated in every template -->
</head>
<body>
    <h1>Login</h1>
</body>
</html>

<!-- register.html - BAD -->
<!DOCTYPE html>
<html>
<head>
    <link href="bootstrap.css" rel="stylesheet">  <!-- Duplicated -->
</head>
<body>
    <h1>Register</h1>
</body>
</html>
```

**Why bad:**
- Violates DRY principle
- If Bootstrap CDN changes, must update every template
- Easy to miss a template during updates
- Inconsistent versions across pages

**Prevention:**
- Create `base.html` with Bootstrap includes
- Child templates extend `base.html`
- Single source of truth for CSS/JS

### Anti-Pattern 2: Hardcoding Grid in Base Template

**What goes wrong:**
```django
<!-- base.html - BAD -->
<body>
    <div class="container">
        <div class="row">
            <div class="col-md-12">
                {% block content %}{% endblock %}
            </div>
        </div>
    </div>
</body>
```

**Why bad:**
- Every page forced into same grid structure
- Can't do full-width backgrounds
- Can't do multi-column layouts
- Inflexible

**Prevention:**
- Keep base template grid-agnostic
- Let child templates define their own grid structure
- Base template only provides framework includes and navbar/footer

### Anti-Pattern 3: No Block for Extra CSS/JS

**What goes wrong:**
```django
<!-- base.html - BAD -->
<head>
    <link href="bootstrap.css" rel="stylesheet">
    <!-- No {% block extra_css %} -->
</head>
<body>
    {% block content %}{% endblock %}
    <script src="bootstrap.js"></script>
    <!-- No {% block extra_js %} -->
</body>
```

**Why bad:**
- Child templates can't add page-specific CSS/JS
- Forces creation of separate CSS files for every page
- Can't use inline `<style>` or `<script>` tags strategically

**Prevention:**
- Always include `{% block extra_css %}` in `<head>` after framework CSS
- Always include `{% block extra_js %}` before `</body>` after framework JS

### Anti-Pattern 4: Deep Inheritance Chains

**What goes wrong:**
```django
base.html → base_section.html → base_subsection.html → base_sub_subsection.html → page.html
```

**Why bad:**
- Hard to debug ("Which template defined this block?")
- Performance overhead (Django walks the inheritance chain)
- Confusing for new developers
- Usually indicates over-engineering

**Prevention:**
- Limit to 2-3 levels: base.html → base_section.html → page.html
- If you need more levels, reconsider architecture
- Use `{% include %}` for reusable components instead

### Anti-Pattern 5: Forgetting `{% extends %}` as First Tag

**What goes wrong:**
```django
<!-- login.html - BAD -->
{% load static %}  <!-- Template tag before extends -->
{% extends "base.html" %}

{% block content %}
    Content here
{% endblock %}
```

**Why bad:**
- Django requires `{% extends %}` as first tag
- Template won't inherit from base
- Cryptic error message

**Prevention:**
- **Always** put `{% extends %}` on line 1
- Put `{% load %}` tags after `{% extends %}`
- Use linter/IDE to catch this

**Correct version:**
```django
<!-- login.html - GOOD -->
{% extends "base.html" %}
{% load static %}

{% block content %}
    Content here
{% endblock %}
```

### Anti-Pattern 6: Not Using Bootstrap Form Classes

**What goes wrong:**
```django
<!-- form.html - BAD -->
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}  <!-- Unstyled Django forms -->
    <button type="submit">Submit</button>
</form>
```

**Why bad:**
- `form.as_p` generates unstyled HTML
- Doesn't use Bootstrap classes (`form-control`, `form-label`, etc.)
- Looks inconsistent with Bootstrap theme
- Can't customize form layout

**Prevention:**
- Manually render form fields with Bootstrap classes
- Use django-crispy-forms with crispy-bootstrap5
- Use django-bootstrap5 template tags

**Manual rendering (recommended for learning):**
```django
<form method="post">
    {% csrf_token %}
    <div class="mb-3">
        <label for="{{ form.username.id_for_label }}" class="form-label">
            Username
        </label>
        {{ form.username.as_widget }}
        {% if form.username.errors %}
            <div class="invalid-feedback">{{ form.username.errors }}</div>
        {% endif %}
    </div>
    <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

**Using django-bootstrap5 (alternative):**
```django
{% load django_bootstrap5 %}

<form method="post">
    {% csrf_token %}
    {% bootstrap_form form %}
    {% bootstrap_button button_type="submit" content="Submit" %}
</form>
```

---

## Bootstrap Components Integration

### Using Bootstrap Components in Templates

Bootstrap 5 provides many components (modals, alerts, tooltips, etc.) that require specific HTML structure and sometimes JavaScript initialization.

#### Alerts (for Django Messages)

```django
<!-- base.html messages block -->
{% block messages %}
{% if messages %}
    <div class="container mt-3">
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        {% endfor %}
    </div>
{% endif %}
{% endblock %}
```

**Django message tags to Bootstrap classes:**
```python
# settings.py
from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}
```

#### Modals

```django
<!-- Trigger button -->
<button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#confirmModal">
    Delete Item
</button>

<!-- Modal markup -->
<div class="modal fade" id="confirmModal" tabindex="-1" aria-labelledby="confirmModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="confirmModalLabel">Confirm Delete</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                Are you sure you want to delete this item?
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <form method="post" action="{% url 'delete_item' item.id %}" class="d-inline">
                    {% csrf_token %}
                    <button type="submit" class="btn btn-danger">Delete</button>
                </form>
            </div>
        </div>
    </div>
</div>
```

#### Cards

```django
<div class="card">
    <div class="card-header">
        Featured
    </div>
    <div class="card-body">
        <h5 class="card-title">Card Title</h5>
        <p class="card-text">Card content goes here.</p>
        <a href="#" class="btn btn-primary">Go somewhere</a>
    </div>
    <div class="card-footer text-muted">
        2 days ago
    </div>
</div>
```

#### Forms with Validation States

```django
<div class="mb-3">
    <label for="email" class="form-label">Email</label>
    <input type="email"
           class="form-control {% if form.email.errors %}is-invalid{% endif %}"
           id="email"
           name="email"
           value="{{ form.email.value|default:'' }}">
    {% if form.email.errors %}
        <div class="invalid-feedback">
            {{ form.email.errors }}
        </div>
    {% else %}
        <div class="form-text">We'll never share your email.</div>
    {% endif %}
</div>
```

---

## Scalability Considerations

### Template Architecture at Different Scales

| Project Size | Template Count | Recommended Structure | Notes |
|--------------|----------------|----------------------|-------|
| Small (1-10 pages) | <20 templates | `base.html` + page templates | Current Pagina Madre |
| Medium (10-50 pages) | 20-100 templates | `base.html` + section bases + page templates | Add `base_auth.html`, `base_dashboard.html` |
| Large (50+ pages) | 100+ templates | Multi-level hierarchy + layout templates | Consider app-level organization |
| Enterprise | 500+ templates | Multiple apps with isolated templates | App-level templates with namespaces |

### When to Add Section Base Templates

**Current structure (sufficient for now):**
```
templates/
├── base.html
├── home.html
├── registration/login.html
└── registration/register.html
```

**Add section bases when:**
- 5+ pages share common layout/structure
- Section needs different navbar/sidebar
- Section has common CSS/JS across pages

**Example expansion:**
```
templates/
├── base.html                     # Site-wide
├── base_auth.html               # Extends base.html (auth pages)
├── base_dashboard.html          # Extends base.html (dashboard pages)
├── home.html                    # Extends base.html
├── registration/
│   ├── login.html               # Extends base_auth.html
│   ├── register.html            # Extends base_auth.html
│   └── password_reset.html      # Extends base_auth.html
└── dashboard/
    ├── home.html                # Extends base_dashboard.html
    ├── profile.html             # Extends base_dashboard.html
    └── settings.html            # Extends base_dashboard.html
```

### Performance Optimization

**Template caching:**
```python
# settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]
```

**When to use cached loader:**
- Production only (not development)
- After template structure is stable
- Provides ~2-3x template rendering speedup

**Bootstrap CDN vs Local:**
- **CDN (recommended for small/medium projects):** Faster initial load due to browser caching, no setup needed
- **Local (for large/enterprise):** Full control over versioning, works offline, can customize Bootstrap

---

## Migration Plan for Current Templates

### Step-by-Step Migration

**Current state analysis:**
- 3 templates: `home.html`, `login.html`, `register.html`
- All standalone (no inheritance)
- No Bootstrap (plain HTML)
- Located in `___/templates/` and `___/templates/registration/`

**Migration steps:**

1. **Create project-level templates directory**
   ```bash
   mkdir templates
   ```

2. **Update settings.py**
   ```python
   TEMPLATES = [
       {
           'BACKEND': 'django.template.backends.django.DjangoTemplates',
           'DIRS': [BASE_DIR / 'templates'],  # Add this
           'APP_DIRS': True,
           ...
       },
   ]
   ```

3. **Create base.html**
   - Include Bootstrap 5 CSS/JS from CDN
   - Define blocks: `title`, `extra_css`, `navbar`, `messages`, `content`, `footer`, `extra_js`
   - Add responsive navbar with user auth status

4. **Move and update templates**
   ```bash
   mv ___/templates/home.html templates/home.html
   mkdir templates/registration
   mv ___/templates/registration/login.html templates/registration/login.html
   mv ___/templates/registration/register.html templates/registration/register.html
   ```

5. **Update each template to extend base.html**
   - Add `{% extends "base.html" %}` as first line
   - Wrap content in `{% block content %}...{% endblock %}`
   - Add Bootstrap classes to existing HTML
   - Add `{% block title %}` for page-specific titles

6. **Test each page**
   - Verify navbar appears
   - Verify Bootstrap styles applied
   - Verify forms still work
   - Verify user auth displayed correctly

7. **Clean up**
   ```bash
   rmdir ___/templates/registration
   rmdir ___/templates
   ```

### Before/After Comparison

**Before (login.html):**
```django
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Pagina Madre</title>
</head>
<body>
    <h1>Login</h1>
    <form method="post">
        {% csrf_token %}
        <p>
            <label for="id_username">Cédula:</label>
            {{ form.username }}
        </p>
        <button type="submit">Login</button>
    </form>
</body>
</html>
```

**After (login.html):**
```django
{% extends "base.html" %}

{% block title %}Login - Pagina Madre{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card shadow-sm">
                <div class="card-body">
                    <h1 class="card-title text-center mb-4">Login</h1>
                    <form method="post">
                        {% csrf_token %}
                        <div class="mb-3">
                            <label for="id_username" class="form-label">Cédula:</label>
                            <input type="text"
                                   name="username"
                                   id="id_username"
                                   class="form-control"
                                   required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Login</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

**Benefits:**
- DRY: Bootstrap includes in one place
- Consistent: navbar/footer on all pages
- Maintainable: change base.html, all pages update
- Styled: Bootstrap classes applied

---

## Sources

**Official Django Documentation:**
- [The Django template language](https://docs.djangoproject.com/en/6.0/ref/templates/language/) - Official template inheritance and block tag documentation
- [Built-in template tags and filters](https://docs.djangoproject.com/en/6.0/ref/templates/builtins/) - Reference for template tags

**Django Best Practices:**
- [Django Best Practices: Template Structure](https://learndjango.com/tutorials/template-structure) - Project-level vs app-level templates
- [Effective Implementation of Django Templates](https://bastakiss.com/blog/django-6/effective-implementation-of-django-templates-structure-inheritance-and-best-practices-800) - Structure and inheritance patterns
- [Handling Django Template Inheritance Best Practices](https://moldstud.com/articles/p-handling-django-template-inheritance-best-practices-for-reusable-and-dry-code) - DRY code practices

**Bootstrap Integration:**
- [Django - Add Bootstrap 5](https://www.w3schools.com/django/django_add_bootstrap5.php) - Basic Bootstrap 5 setup
- [How to Integrate Bootstrap 5 in Django](https://studygyaan.com/django/how-to-integrate-bootstrap-template-in-django) - CDN integration guide
- [django-bootstrap5 Documentation](https://django-bootstrap5.readthedocs.io/) - Official django-bootstrap5 package
- [django-bootstrap5 PyPI](https://pypi.org/project/django-bootstrap5/) - Package information and version history

**Template Architecture Patterns:**
- [An Architecture for Django Templates](https://oncampus.oberlin.edu/webteam/2012/09/architecture-django-templates) - Block naming conventions and layout templates
- [Django Template Blocks](https://www.compilenrun.com/docs/framework/django/django-templates/django-template-blocks/) - Block usage patterns
- [Templates & Blocks Reference - Django AdminLTE](https://django-adminlte2.readthedocs.io/en/latest/templates_and_blocks.html) - Advanced block structure

**Community Resources:**
- [GitHub: django-bootstrap-base-template](https://github.com/gunthercox/django-bootstrap-base-template) - Example base templates
- [GitHub: plumdog/django-bootstrap-base-template](https://github.com/plumdog/django-bootstrap-base-template) - Another example implementation
- [Understanding Django template inheritance](https://dev.to/doridoro/understanding-django-template-inheritance-d8c) - Tutorial on template inheritance

**Confidence Level:** HIGH
- Official Django documentation verified
- Bootstrap integration patterns from multiple authoritative sources
- Community conventions documented in multiple resources
- Current as of January 2026 (Bootstrap 5, Django 5/6)