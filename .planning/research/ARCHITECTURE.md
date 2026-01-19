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

## v1.2 Referral System Architecture

**Added:** 2026-01-19 for v1.2 milestone

### Model Design

#### Recommendation: Extend CustomUser (not separate model)

**Why extend CustomUser:**
- Each user has exactly one referral goal and one referrer (1:1 relationship)
- Data always accessed together (profile page shows user + goal)
- Simpler queries: `user.referral_goal` vs `user.referralprofile.goal`
- Migration is straightforward on existing table

**Add to CustomUser:**

```python
# accounts/models.py additions

class CustomUser(AbstractUser):
    # ... existing fields (cedula, nombre_completo, phone, data_policy_accepted)

    # NEW: Referral fields
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals'
    )
    referral_goal = models.PositiveIntegerField(
        default=5,
        verbose_name='Meta de referidos'
    )
    referral_code = models.CharField(
        max_length=12,
        unique=True,
        blank=True,
        verbose_name='Codigo de referido'
    )

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self._generate_referral_code()
        super().save(*args, **kwargs)

    def _generate_referral_code(self):
        """Generate unique referral code based on cedula + random suffix"""
        import secrets
        return f"{self.cedula[:4]}{secrets.token_hex(4)}"

    @property
    def referral_count(self):
        """Count of users referred by this user"""
        return self.referrals.count()

    @property
    def referral_progress_percent(self):
        """Progress toward goal as percentage (capped at 100)"""
        if self.referral_goal == 0:
            return 100
        return min(100, int((self.referral_count / self.referral_goal) * 100))
```

#### Data Relationships

```
CustomUser
    |
    +-- referred_by --> CustomUser (nullable FK to self)
    |
    +-- referrals --> [CustomUser, ...] (reverse relation: users I referred)
```

**Query patterns:**
- Get who referred me: `user.referred_by`
- Get users I referred: `user.referrals.all()`
- Count my referrals: `user.referral_count` (property)

#### Why NOT a separate Referral model

A separate model would be needed if:
- Tracking multiple referral events per user (not our case)
- Storing referral metadata (timestamp, status, rewards)
- Referral-specific business logic

Our requirements are simpler: just track who referred whom. Self-referential FK is cleaner.

---

### URL Structure

#### New Routes (all within accounts app)

| URL | Name | View | Purpose |
|-----|------|------|---------|
| `/profile/` | `profile` | `profile_view` | Edit user info + set goal |
| `/referidos/` | `referidos` | `referidos_view` | Table of referred users |

#### Modified Routes

| URL | Change |
|-----|--------|
| `/register/` | Accept `?ref=CODE` parameter |

#### Full URL Configuration

```python
# accounts/urls.py (updated)

urlpatterns = [
    path('', home, name='home'),                          # existing
    path('register/', register, name='register'),          # existing (modified)
    path('login/', CustomLoginView.as_view(), name='login'),  # existing
    path('logout/', LogoutView.as_view(), name='logout'),  # existing
    path('profile/', profile_view, name='profile'),        # NEW
    path('referidos/', referidos_view, name='referidos'),  # NEW
]
```

#### Referral Link Format

```
https://example.com/register/?ref=1234abcd5678
```

- Parameter: `ref` (short, memorable)
- Code: 12-char unique code per user
- Example: First 4 chars of cedula + 8 random hex chars

---

### View Organization

#### New Views Required

```python
# accounts/views.py additions

@login_required
def profile_view(request):
    """Edit user profile and referral goal"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})


@login_required
def referidos_view(request):
    """Display table of referred users"""
    referidos = request.user.referrals.all().order_by('-date_joined')
    return render(request, 'referidos.html', {'referidos': referidos})
```

#### Modified Views

**register() must capture referral code:**

```python
def register(request):
    referral_code = request.GET.get('ref')
    referrer = None

    if referral_code:
        try:
            referrer = CustomUser.objects.get(referral_code=referral_code)
        except CustomUser.DoesNotExist:
            pass  # Invalid code, proceed without referrer

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.referred_by = referrer  # Set referrer before save
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {
        'form': form,
        'referrer_name': referrer.nombre_completo if referrer else None
    })
```

**home() needs referral context:**

```python
@login_required
def home(request):
    """Home page with referral stats"""
    user = request.user
    referral_link = request.build_absolute_uri(
        f"/register/?ref={user.referral_code}"
    )
    return render(request, 'home.html', {
        'user': user,
        'referral_link': referral_link,
        'referral_count': user.referral_count,
        'referral_goal': user.referral_goal,
        'referral_progress': user.referral_progress_percent,
    })
```

#### New Forms Required

```python
# accounts/forms.py additions

class ProfileForm(forms.ModelForm):
    """Form for editing profile and referral goal"""

    class Meta:
        model = CustomUser
        fields = ['nombre_completo', 'phone', 'referral_goal']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'referral_goal': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '1000'
            }),
        }

class PasswordChangeForm(forms.Form):
    """Separate form for password changes"""
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
```

---

### Template Structure

#### New Templates

| Template | Extends | Purpose |
|----------|---------|---------|
| `templates/profile.html` | `base.html` | Profile edit form |
| `templates/referidos.html` | `base.html` | Referral table |

#### Template Hierarchy

```
templates/
    base.html                    # existing - Bootstrap head/body structure
    home.html                    # existing - UPDATE: add referral stats + nav links
    profile.html                 # NEW - profile edit form
    referidos.html               # NEW - referral table
    includes/
        navbar.html              # NEW - extracted navbar for reuse
    registration/
        login.html               # existing - no changes
        register.html            # existing - UPDATE: show referrer name if present
```

#### Navbar Extraction

Current home.html has navbar inline. Extract to include for DRY:

```html
<!-- templates/includes/navbar.html -->
<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
        <a class="navbar-brand" href="{% url 'home' %}">Pagina Madre</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav me-auto">
                <li class="nav-item">
                    <a class="nav-link {% if request.resolver_match.url_name == 'home' %}active{% endif %}"
                       href="{% url 'home' %}">Inicio</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link {% if request.resolver_match.url_name == 'referidos' %}active{% endif %}"
                       href="{% url 'referidos' %}">Mis Referidos</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link {% if request.resolver_match.url_name == 'profile' %}active{% endif %}"
                       href="{% url 'profile' %}">Perfil</a>
                </li>
            </ul>
            <ul class="navbar-nav ms-auto align-items-center">
                <li class="nav-item">
                    <span class="nav-link text-light">{{ user.nombre_completo }}</span>
                </li>
                <li class="nav-item">
                    <form method="post" action="{% url 'logout' %}">
                        {% csrf_token %}
                        <button type="submit" class="btn btn-outline-light btn-sm">
                            Cerrar Sesion
                        </button>
                    </form>
                </li>
            </ul>
        </div>
    </div>
</nav>
```

#### Profile Page Structure

```html
<!-- templates/profile.html -->
{% extends 'base.html' %}

{% block navbar %}
{% include 'includes/navbar.html' %}
{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-lg-6">
            <div class="card shadow">
                <div class="card-header">
                    <h4>Mi Perfil</h4>
                </div>
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        {{ form.as_div }}
                        <button type="submit" class="btn btn-primary">Guardar Cambios</button>
                    </form>
                </div>
            </div>

            <!-- Separate card for password change -->
            <div class="card shadow mt-4">
                <div class="card-header">
                    <h4>Cambiar Contrasena</h4>
                </div>
                <div class="card-body">
                    <!-- Password change form -->
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

#### Referidos Page Structure

```html
<!-- templates/referidos.html -->
{% extends 'base.html' %}

{% block navbar %}
{% include 'includes/navbar.html' %}
{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row">
        <div class="col-12">
            <div class="card shadow">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h4>Mis Referidos</h4>
                    <span class="badge bg-primary">{{ referidos.count }} referidos</span>
                </div>
                <div class="card-body">
                    {% if referidos %}
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Nombre</th>
                                    <th>Cedula</th>
                                    <th>Telefono</th>
                                    <th>Fecha de Registro</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for referido in referidos %}
                                <tr>
                                    <td>{{ referido.nombre_completo }}</td>
                                    <td>{{ referido.cedula }}</td>
                                    <td>{{ referido.phone }}</td>
                                    <td>{{ referido.date_joined|date:"d/m/Y" }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <p class="text-muted">Aun no tienes referidos. Comparte tu link!</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

#### Home Page Updates

Add to existing home.html:
1. Referral stats card (count, progress bar, goal)
2. Shareable link with copy-to-clipboard button
3. Navigation links via navbar include

---

### Component Boundaries

#### What Talks to What

```
Browser Request
      |
      v
+------------------+
|  Django URLs     |  /register/?ref=CODE
|  (accounts/urls) |  /profile/
|                  |  /referidos/
+------------------+
      |
      v
+------------------+
|  Views           |  Handles request, calls model, returns template
|  (accounts/views)|
+------------------+
      |
      +-----> Forms (validation, widget styling)
      |
      +-----> Models (data access, computed properties)
      |
      v
+------------------+
|  Templates       |  Renders HTML with context
|  (templates/)    |
+------------------+
      |
      v
Browser Response
```

#### Data Flow: Registration with Referral

```
1. User clicks referral link: /register/?ref=1234abcd5678
2. register() extracts ref parameter
3. Query CustomUser by referral_code
4. If found, store referrer for later
5. User fills and submits form
6. On save, set referred_by = referrer
7. New user created with referrer relationship
8. Referrer's referral_count property automatically reflects new referral
```

#### Data Flow: Viewing Referral Progress

```
1. User visits home page
2. home() view queries:
   - user.referral_count (COUNT on referrals relation)
   - user.referral_goal
   - user.referral_progress_percent (computed property)
3. Template renders progress bar and stats
```

---

### Build Order

Based on dependencies, build in this sequence:

#### Phase 1: Model Foundation

**Dependencies:** None
**Outputs:** Migration file, model ready for use

1. Add fields to CustomUser model:
   - `referred_by` (FK to self)
   - `referral_goal` (PositiveIntegerField)
   - `referral_code` (CharField, unique)
2. Add model methods:
   - `_generate_referral_code()`
   - `referral_count` property
   - `referral_progress_percent` property
3. Create and run migration
4. Generate referral codes for existing users (data migration)

#### Phase 2: Registration Capture

**Dependencies:** Phase 1 (referral_code field exists)
**Outputs:** Registration captures referrer

1. Update register() view to extract `ref` parameter
2. Query referrer by referral_code
3. Set `referred_by` on new user save
4. Update register.html to show referrer name (optional UX)

#### Phase 3: Home Page Referral Display

**Dependencies:** Phase 1 (referral_count works)
**Outputs:** Home shows referral stats and link

1. Update home() view context with referral data
2. Add referral stats card to home.html
3. Add shareable link with copy-to-clipboard button
4. Add progress bar toward goal

#### Phase 4: Navigation Structure

**Dependencies:** None (can parallelize with Phase 3)
**Outputs:** Navbar available for all authenticated pages

1. Create `templates/includes/navbar.html`
2. Refactor home.html to use navbar include
3. Add nav links: Inicio, Mis Referidos, Perfil

#### Phase 5: Profile Page

**Dependencies:** Phase 4 (navbar include exists)
**Outputs:** Profile page functional

1. Create ProfileForm in forms.py
2. Create profile_view in views.py
3. Add URL route
4. Create profile.html template
5. Add password change section (separate form)

#### Phase 6: Referidos Page

**Dependencies:** Phase 4 (navbar include exists)
**Outputs:** Referidos page functional

1. Create referidos_view in views.py
2. Add URL route
3. Create referidos.html template with table

#### Suggested Phase Grouping for Roadmap

| Roadmap Phase | Tasks | Rationale |
|---------------|-------|-----------|
| **Phase 1: Referral Model** | Build phases 1-2 | Foundation must exist first |
| **Phase 2: Home Referral UI** | Build phase 3 | Core feature visible to user |
| **Phase 3: Navigation + Profile** | Build phases 4-5 | Enables profile editing |
| **Phase 4: Referidos Page** | Build phase 6 | Completes feature set |

---

### Anti-Patterns to Avoid

#### 1. Circular Import Issues

**Risk:** Models importing from views, views importing from forms importing from models
**Prevention:** Keep imports directional: views import models, forms import models, templates are independent

#### 2. N+1 Query Problems

**Risk:** Looping over referrals and accessing related data
**Prevention:** Use `select_related()` and `prefetch_related()` in views

```python
# BAD
referidos = request.user.referrals.all()
for r in referidos:
    print(r.nombre_completo)  # N queries

# GOOD
referidos = request.user.referrals.select_related().all()
```

#### 3. Referral Code Collisions

**Risk:** Two users get same referral code
**Prevention:**
- Use `unique=True` constraint on field
- Generate with enough entropy (8 hex chars = 4 billion combinations)
- Handle IntegrityError and regenerate if collision

#### 4. Self-Referral

**Risk:** User refers themselves (creates loop)
**Prevention:** Validate in registration that referrer != new user

```python
if referrer and referrer.cedula == form.cleaned_data['cedula']:
    referrer = None  # Don't allow self-referral
```

---

## Recommended Architecture (Original v1.0/v1.1)

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
- 4 templates: `base.html`, `home.html`, `registration/login.html`, `registration/register.html`
- Template inheritance implemented
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
```

**Why bad:**
- Violates DRY principle
- If Bootstrap CDN changes, must update every template

**Prevention:**
- Create `base.html` with Bootstrap includes
- Child templates extend `base.html`

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
- Can't have full-width pages

**Prevention:**
- Keep base template grid-agnostic
- Let child templates define their own grid structure

### Anti-Pattern 3: Deep Inheritance Chains

**What goes wrong:**
```
base.html -> base_section.html -> base_subsection.html -> page.html
```

**Why bad:**
- Hard to debug ("Which template defined this block?")
- Performance overhead

**Prevention:**
- Limit to 2-3 levels
- Use `{% include %}` for reusable components instead

---

## Sources

**Existing Codebase:**
- `/Users/Diego.Lopezruiz/Documents/Repositories/Pagina-Madre-1/___/accounts/models.py`
- `/Users/Diego.Lopezruiz/Documents/Repositories/Pagina-Madre-1/___/accounts/views.py`
- `/Users/Diego.Lopezruiz/Documents/Repositories/Pagina-Madre-1/___/templates/`

**Django Documentation:**
- Django ForeignKey to self pattern: Django 4.2 documentation (models.ForeignKey with 'self')
- Template inheritance: Django template language documentation

**Project Requirements:**
- `.planning/PROJECT.md` v1.2 requirements section

---

## Confidence Assessment

| Area | Confidence | Reason |
|------|------------|--------|
| v1.2 Model design | HIGH | Standard Django self-referential FK pattern, verified against existing model |
| v1.2 URL structure | HIGH | Follows existing accounts/urls.py pattern |
| v1.2 View organization | HIGH | Matches existing views.py patterns |
| v1.2 Template structure | HIGH | Extends existing template inheritance |
| v1.2 Build order | HIGH | Based on clear dependencies |
| Original template patterns | HIGH | Official Django documentation verified |
| Bootstrap integration | HIGH | Multiple authoritative sources |
