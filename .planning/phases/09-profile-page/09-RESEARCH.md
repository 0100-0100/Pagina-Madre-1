# Phase 9: Profile Page - Research

**Researched:** 2026-01-19
**Domain:** Django User Profile Editing, Password Change, Bootstrap 5 Forms
**Confidence:** HIGH

## Summary

This phase implements a profile editing page allowing users to update their nombre_completo, telefono, and referral goal, plus a separate password change page. The profile page replaces the existing placeholder route at `/perfil/`. The implementation follows established patterns from the register page (real-time validation, input filtering, debounce) and home page (toast notifications, card layout).

The profile editing uses Django's standard form handling with a custom ModelForm for the editable fields. The password change functionality leverages Django's built-in `PasswordChangeView` and `PasswordChangeForm` which handle old password verification and new password validation automatically. Django's messages framework integrates with Bootstrap toasts for success/error feedback across page redirects.

The form layout uses a single centered card (50-60% width) matching the home page style. Fields are displayed in order: Cedula (read-only text), Nombre Completo, Telefono, Meta de Referidos, then a "Cambiar Contrasena" button linking to the separate password change page.

**Primary recommendation:** Use a function-based view with a custom ProfileForm (ModelForm) for profile editing, Django's built-in `PasswordChangeView` with custom template for password change, and the messages framework with Bootstrap toasts for feedback on save/redirect.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Django Forms | 4.2 (built-in) | Form handling, validation | Built-in, handles CSRF, validation, error display |
| Django ModelForm | 4.2 (built-in) | Form from model fields | Auto-generates form from model, handles save() |
| PasswordChangeView | 4.2 (built-in) | Password change handling | Secure, validates old password, uses password validators |
| PasswordChangeForm | 4.2 (built-in) | Password change form | Built-in validation for old password + new password match |
| Django Messages | 4.2 (built-in) | Flash messages across redirects | Session-based, integrates with Bootstrap alerts/toasts |
| Bootstrap 5 | 5.3.8 | UI components, form styling | Already in project via CDN |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| update_session_auth_hash | 4.2 (built-in) | Keep session valid after password change | After successful password change to avoid logout |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Function-based view | UpdateView (CBV) | FBV simpler for single-model editing with custom logic |
| Custom password change | Custom view with set_password() | Built-in handles validation, security, session hash update |
| Messages framework | Session variables | Messages auto-clear after display, typed levels |

**Installation:**
```bash
# No additional packages required
# All components are Django built-in + existing Bootstrap CDN
```

## Architecture Patterns

### Recommended Project Structure
```
___/
├── accounts/
│   ├── forms.py           # Add ProfileForm (ModelForm)
│   ├── views.py           # Add profile_view, CustomPasswordChangeView
│   └── urls.py            # Update perfil route, add cambiar-password route
└── templates/
    ├── profile.html       # Profile editing page
    └── registration/
        └── password_change.html  # Password change page
```

### Pattern 1: Profile ModelForm for Specific Fields
**What:** ModelForm that exposes only the editable fields (nombre_completo, phone, referral_goal).
**When to use:** When editing a subset of model fields with custom validation.
**Example:**
```python
# Source: Django ModelForm documentation
from django import forms
from .models import CustomUser

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['nombre_completo', 'phone', 'referral_goal']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo',
                'maxlength': '60'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numero de telefono',
                'inputmode': 'numeric',
                'maxlength': '10'
            }),
            'referral_goal': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }
        labels = {
            'nombre_completo': 'Nombre Completo',
            'phone': 'Telefono',
            'referral_goal': 'Meta de Referidos',
        }
```

### Pattern 2: Profile View with Form Instance Binding
**What:** Function-based view that binds form to current user instance for editing.
**When to use:** When editing the logged-in user's own data.
**Example:**
```python
# Source: Django form handling patterns
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileForm

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('perfil')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'profile.html', {'form': form})
```

### Pattern 3: Custom PasswordChangeView with Custom Template
**What:** Subclass PasswordChangeView to use custom template and redirect URL.
**When to use:** When using Django's built-in password change with custom styling.
**Example:**
```python
# Source: Django PasswordChangeView documentation
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse_lazy
from django.contrib import messages

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change.html'
    success_url = reverse_lazy('perfil')
    form_class = PasswordChangeForm

    def form_valid(self, form):
        messages.success(self.request, 'Contrasena actualizada correctamente')
        return super().form_valid(form)
```

**Key points:**
- `PasswordChangeForm` requires old password before allowing change
- Built-in view handles `update_session_auth_hash()` automatically
- `success_url` redirects back to profile after successful change

### Pattern 4: Bootstrap Form Styling with Custom Attributes
**What:** Adding Bootstrap classes to form fields via widget attrs.
**When to use:** When manually rendering form fields with Bootstrap styling.
**Example:**
```python
# In forms.py __init__ method for inherited fields
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contrasena actual'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nueva contrasena'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contrasena'
        })
```

### Pattern 5: Messages Framework with Bootstrap Toasts
**What:** Django messages displayed as Bootstrap toast notifications.
**When to use:** For non-blocking success/error feedback after form submission.
**Example:**
```html
<!-- Toast container in template -->
<div class="toast-container position-fixed top-0 end-0 p-3">
    {% for message in messages %}
    <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true"
         data-bs-autohide="true" data-bs-delay="3000">
        <div class="toast-header">
            {% if message.tags == 'success' %}
            <i class="bi bi-check-circle text-success me-2"></i>
            <strong class="me-auto">Exito</strong>
            {% elif message.tags == 'error' %}
            <i class="bi bi-exclamation-circle text-danger me-2"></i>
            <strong class="me-auto">Error</strong>
            {% endif %}
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">{{ message }}</div>
    </div>
    {% endfor %}
</div>
```

**JavaScript to auto-show toasts:**
```javascript
// Initialize toasts on page load
document.querySelectorAll('.toast').forEach(function(toastEl) {
    const toast = new bootstrap.Toast(toastEl, { autohide: true, delay: 3000 });
    toast.show();
});
```

### Anti-Patterns to Avoid
- **Editing user fields without instance binding:** Always pass `instance=request.user` to form to populate existing values.
- **Custom password change without old password:** Security risk. Use `PasswordChangeForm` which requires old password.
- **Forgetting update_session_auth_hash:** User gets logged out after password change. PasswordChangeView handles this automatically.
- **Hardcoding user ID in URL:** Always use `request.user` for current user's profile.
- **Mixing GET and POST data:** Don't use `request.REQUEST` (deprecated). Check `request.method` explicitly.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Password change form | Custom form with set_password() | PasswordChangeForm + PasswordChangeView | Validates old password, checks password strength, handles session |
| Form error display | Manual error HTML | Bootstrap's is-invalid class + invalid-feedback div | Consistent styling, accessibility |
| Success messages | Custom session variable | Django messages framework | Auto-clears, typed levels, template iteration |
| Model form fields | Manual field declarations | ModelForm with fields list | Auto-generates from model, handles save() |
| Session invalidation on password change | Manual session handling | update_session_auth_hash() (auto in PasswordChangeView) | Handles all edge cases |

**Key insight:** Django's PasswordChangeView handles security concerns (old password verification, session hash update) that are easy to forget in custom implementations. Use the built-in view with custom template.

## Common Pitfalls

### Pitfall 1: User Logged Out After Password Change
**What goes wrong:** User successfully changes password but is immediately logged out.
**Why it happens:** Django invalidates all sessions when password changes. Current session needs to be updated.
**How to avoid:**
- Use `PasswordChangeView` which calls `update_session_auth_hash()` automatically
- If custom view, call `update_session_auth_hash(request, user)` after `form.save()`
**Warning signs:** User complains about being logged out after password change.

### Pitfall 2: Form Not Showing Current Values
**What goes wrong:** Profile form shows empty fields instead of current user data.
**Why it happens:** Form instantiated without `instance` parameter.
**How to avoid:**
```python
# GET request - show current values
form = ProfileForm(instance=request.user)

# POST request - bind to same instance for update
form = ProfileForm(request.POST, instance=request.user)
```
**Warning signs:** All fields empty on page load, user loses data when submitting.

### Pitfall 3: Toast Not Showing on Redirect
**What goes wrong:** Message added in view but toast doesn't appear on redirected page.
**Why it happens:** Messages stored in session but template doesn't display them, or JavaScript doesn't initialize toasts.
**How to avoid:**
- Include messages display block in template
- Initialize Bootstrap Toast JS on page load for messages
- Check `{% if messages %}` block exists in template
**Warning signs:** No visual feedback after save, message appears only on next page refresh.

### Pitfall 4: Read-Only Field Submitted in Form
**What goes wrong:** Cedula field (meant to be display-only) gets submitted and causes validation errors.
**Why it happens:** Including cedula in form fields even though it shouldn't be editable.
**How to avoid:**
- Don't include cedula in ProfileForm fields
- Display cedula as plain text in template, not as form field
```html
<div class="mb-3">
    <label class="form-label">Cedula</label>
    <p class="form-control-plaintext">{{ user.cedula }}</p>
</div>
```
**Warning signs:** Validation errors on cedula, or cedula changes unexpectedly.

### Pitfall 5: referral_goal Accepts Negative Numbers
**What goes wrong:** User enters negative referral goal, breaks progress calculation.
**Why it happens:** NumberInput allows negative by default, model field allows it.
**How to avoid:**
- Use `PositiveIntegerField` in model (already done per models.py)
- Add `min="0"` to NumberInput widget attrs
- Add `clean_referral_goal()` validation to form
```python
def clean_referral_goal(self):
    goal = self.cleaned_data.get('referral_goal')
    if goal is not None and goal < 0:
        raise ValidationError('La meta debe ser 0 o mayor')
    return goal
```
**Warning signs:** Progress bar shows negative or over 100%.

### Pitfall 6: Password Change Page Accessible Without Login
**What goes wrong:** Non-authenticated user can access password change page.
**Why it happens:** PasswordChangeView is login-required by default, but custom implementation might miss this.
**How to avoid:**
- `PasswordChangeView` inherits `LoginRequiredMixin` - already protected
- If function-based view, use `@login_required` decorator
- Existing `LoginRequiredMiddleware` should catch this anyway
**Warning signs:** Redirect to login instead of password change, or 500 error about anonymous user.

## Code Examples

Verified patterns from official sources:

### ProfileForm (forms.py)
```python
# Source: Django ModelForm documentation + existing project patterns
import re
from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['nombre_completo', 'phone', 'referral_goal']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo',
                'maxlength': '60'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numero de telefono',
                'inputmode': 'numeric',
                'maxlength': '10'
            }),
            'referral_goal': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }
        labels = {
            'nombre_completo': 'Nombre Completo',
            'phone': 'Telefono',
            'referral_goal': 'Meta de Referidos',
        }

    def clean_nombre_completo(self):
        """Validate nombre_completo: letters, spaces, accents only, max 60 chars"""
        nombre = self.cleaned_data.get('nombre_completo', '')
        if not re.match(r'^[a-zA-ZaeiounuAEIOUNU\s\'-]+$', nombre):
            raise ValidationError('El nombre solo puede contener letras y espacios')
        if len(nombre) < 2:
            raise ValidationError('El nombre debe tener al menos 2 caracteres')
        if len(nombre) > 60:
            raise ValidationError('El nombre no puede exceder 60 caracteres')
        return nombre

    def clean_phone(self):
        """Validate phone: 10 digits only"""
        phone = self.cleaned_data.get('phone', '')
        if not phone.isdigit():
            raise ValidationError('El telefono solo puede contener numeros')
        if len(phone) != 10:
            raise ValidationError('El telefono debe tener 10 digitos')
        return phone

    def clean_referral_goal(self):
        """Validate referral_goal: positive integer"""
        goal = self.cleaned_data.get('referral_goal')
        if goal is not None and goal < 0:
            raise ValidationError('La meta debe ser 0 o mayor')
        return goal
```

### CustomPasswordChangeForm (forms.py)
```python
# Source: Django PasswordChangeForm + Bootstrap styling pattern from project
from django.contrib.auth.forms import PasswordChangeForm

class CustomPasswordChangeForm(PasswordChangeForm):
    """PasswordChangeForm with Bootstrap 5 styling"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contrasena actual'
        })
        self.fields['old_password'].label = 'Contrasena Actual'

        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nueva contrasena'
        })
        self.fields['new_password1'].label = 'Nueva Contrasena'

        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contrasena'
        })
        self.fields['new_password2'].label = 'Confirmar Nueva Contrasena'
```

### Profile View (views.py)
```python
# Source: Django form handling patterns
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileForm

@login_required
def profile_view(request):
    """Profile editing view."""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'profile.html', {
        'form': form,
        'user': request.user
    })
```

### Custom Password Change View (views.py)
```python
# Source: Django PasswordChangeView documentation
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomPasswordChangeForm

class CustomPasswordChangeView(PasswordChangeView):
    """Password change view with custom template and redirect."""
    template_name = 'registration/password_change.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('perfil')

    def form_valid(self, form):
        messages.success(self.request, 'Contrasena actualizada correctamente')
        return super().form_valid(form)
```

### URL Configuration (urls.py)
```python
# Source: Django URL patterns
from django.urls import path
from .views import profile_view, CustomPasswordChangeView

urlpatterns = [
    # ... existing routes ...
    path('perfil/', profile_view, name='perfil'),
    path('cambiar-password/', CustomPasswordChangeView.as_view(), name='password_change'),
]
```

### Profile Template (profile.html)
```html
{% extends 'base.html' %}

{% block title %}Perfil - Pagina Madre{% endblock %}

{% block navbar %}
<!-- Same navbar as home.html -->
{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-lg-6 col-md-8 col-12">
            <div class="card shadow">
                <div class="card-body p-4">
                    <h4 class="card-title text-center mb-4">Mi Perfil</h4>

                    <!-- Error summary alert -->
                    {% if form.non_field_errors %}
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        {% for error in form.non_field_errors %}
                        {{ error }}
                        {% endfor %}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                    {% endif %}

                    <form method="post" novalidate>
                        {% csrf_token %}

                        <!-- Cedula (read-only) -->
                        <div class="mb-3">
                            <label class="form-label">Cedula</label>
                            <p class="form-control-plaintext bg-light px-3 py-2 rounded">
                                {{ user.cedula }}
                            </p>
                        </div>

                        <!-- Nombre Completo -->
                        <div class="mb-3">
                            <label for="id_nombre_completo" class="form-label">
                                {{ form.nombre_completo.label }}
                            </label>
                            <input type="text"
                                   name="nombre_completo"
                                   class="form-control{% if form.nombre_completo.errors %} is-invalid{% endif %}"
                                   id="id_nombre_completo"
                                   value="{{ form.nombre_completo.value|default:'' }}"
                                   maxlength="60"
                                   required>
                            <div class="invalid-feedback">
                                {% if form.nombre_completo.errors %}
                                {{ form.nombre_completo.errors.0 }}
                                {% else %}
                                El nombre solo puede contener letras y espacios
                                {% endif %}
                            </div>
                        </div>

                        <!-- Telefono -->
                        <div class="mb-3">
                            <label for="id_phone" class="form-label">
                                {{ form.phone.label }}
                            </label>
                            <input type="text"
                                   name="phone"
                                   class="form-control{% if form.phone.errors %} is-invalid{% endif %}"
                                   id="id_phone"
                                   value="{{ form.phone.value|default:'' }}"
                                   inputmode="numeric"
                                   maxlength="10"
                                   required>
                            <div class="invalid-feedback">
                                {% if form.phone.errors %}
                                {{ form.phone.errors.0 }}
                                {% else %}
                                El telefono debe tener 10 digitos
                                {% endif %}
                            </div>
                        </div>

                        <!-- Meta de Referidos -->
                        <div class="mb-3">
                            <label for="id_referral_goal" class="form-label">
                                {{ form.referral_goal.label }}
                            </label>
                            <input type="number"
                                   name="referral_goal"
                                   class="form-control{% if form.referral_goal.errors %} is-invalid{% endif %}"
                                   id="id_referral_goal"
                                   value="{{ form.referral_goal.value|default:'10' }}"
                                   min="0">
                            <div class="invalid-feedback">
                                {% if form.referral_goal.errors %}
                                {{ form.referral_goal.errors.0 }}
                                {% else %}
                                La meta debe ser 0 o mayor
                                {% endif %}
                            </div>
                        </div>

                        <!-- Password Change Link -->
                        <div class="mb-4">
                            <a href="{% url 'password_change' %}" class="btn btn-outline-secondary">
                                <i class="bi bi-lock"></i> Cambiar Contrasena
                            </a>
                        </div>

                        <!-- Submit Button -->
                        <button type="submit" class="btn btn-primary w-100">
                            Guardar
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Toast Container for Messages -->
<div class="toast-container position-fixed top-0 end-0 p-3">
    {% for message in messages %}
    <div class="toast" role="alert" aria-live="assertive" aria-atomic="true"
         data-bs-autohide="true" data-bs-delay="3000">
        <div class="toast-header">
            {% if message.tags == 'success' %}
            <i class="bi bi-check-circle text-success me-2"></i>
            <strong class="me-auto">Exito</strong>
            {% else %}
            <i class="bi bi-exclamation-circle text-danger me-2"></i>
            <strong class="me-auto">Error</strong>
            {% endif %}
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">{{ message }}</div>
    </div>
    {% endfor %}
</div>
{% endblock %}

{% block extra_js %}
<script>
(function() {
    'use strict';

    // Initialize toasts from messages
    document.querySelectorAll('.toast').forEach(function(toastEl) {
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
    });

    // Real-time validation setup (reuse from register.html patterns)
    // ... validation code ...
})();
</script>
{% endblock %}
```

### Password Change Template (password_change.html)
```html
{% extends 'base.html' %}

{% block title %}Cambiar Contrasena - Pagina Madre{% endblock %}

{% block navbar %}
<!-- Same navbar as home.html -->
{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-lg-5 col-md-6 col-12">
            <div class="card shadow">
                <div class="card-body p-4">
                    <h4 class="card-title text-center mb-4">Cambiar Contrasena</h4>

                    {% if form.non_field_errors %}
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        {% for error in form.non_field_errors %}
                        {{ error }}
                        {% endfor %}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                    {% endif %}

                    <form method="post" novalidate>
                        {% csrf_token %}

                        <div class="mb-3">
                            <label for="id_old_password" class="form-label">
                                Contrasena Actual
                            </label>
                            <input type="password"
                                   name="old_password"
                                   class="form-control{% if form.old_password.errors %} is-invalid{% endif %}"
                                   id="id_old_password"
                                   placeholder="Contrasena actual"
                                   required>
                            <div class="invalid-feedback">
                                {% if form.old_password.errors %}
                                {{ form.old_password.errors.0 }}
                                {% else %}
                                Ingrese su contrasena actual
                                {% endif %}
                            </div>
                        </div>

                        <div class="mb-3">
                            <label for="id_new_password1" class="form-label">
                                Nueva Contrasena
                            </label>
                            <input type="password"
                                   name="new_password1"
                                   class="form-control{% if form.new_password1.errors %} is-invalid{% endif %}"
                                   id="id_new_password1"
                                   placeholder="Nueva contrasena"
                                   required>
                            <div class="invalid-feedback">
                                {% if form.new_password1.errors %}
                                {{ form.new_password1.errors.0 }}
                                {% else %}
                                La contrasena debe tener al menos 8 caracteres
                                {% endif %}
                            </div>
                        </div>

                        <div class="mb-4">
                            <label for="id_new_password2" class="form-label">
                                Confirmar Nueva Contrasena
                            </label>
                            <input type="password"
                                   name="new_password2"
                                   class="form-control{% if form.new_password2.errors %} is-invalid{% endif %}"
                                   id="id_new_password2"
                                   placeholder="Confirmar nueva contrasena"
                                   required>
                            <div class="invalid-feedback">
                                {% if form.new_password2.errors %}
                                {{ form.new_password2.errors.0 }}
                                {% else %}
                                Las contrasenas deben coincidir
                                {% endif %}
                            </div>
                        </div>

                        <div class="d-flex gap-2">
                            <a href="{% url 'perfil' %}" class="btn btn-outline-secondary flex-grow-1">
                                Cancelar
                            </a>
                            <button type="submit" class="btn btn-primary flex-grow-1">
                                Cambiar Contrasena
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Real-Time Validation JavaScript (profile.html)
```javascript
// Source: Existing register.html patterns
(function() {
    'use strict';

    // Initialize toasts from messages
    document.querySelectorAll('.toast').forEach(function(toastEl) {
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
    });

    // Debounce function
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Validate nombre (letters, spaces, accents only)
    function validateNombre(input) {
        const value = input.value.trim();
        const isValid = /^[a-zA-ZaeiounuAEIOUNU\s'-]+$/.test(value) &&
                        value.length >= 2 && value.length <= 60;
        const isEmpty = value === '';

        if (isEmpty) {
            input.classList.remove('is-invalid', 'is-valid');
        } else if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        }
    }

    // Validate phone (10 numeric digits)
    function validatePhone(input) {
        const value = input.value.trim();
        const isValid = /^[0-9]{10}$/.test(value);
        const isEmpty = value === '';

        if (isEmpty) {
            input.classList.remove('is-invalid', 'is-valid');
        } else if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        }
    }

    // Filter numeric input
    function filterNumericInput(input, maxLength) {
        const numericOnly = input.value.replace(/[^0-9]/g, '');
        input.value = numericOnly.slice(0, maxLength);
    }

    // Get form fields
    const nombreField = document.getElementById('id_nombre_completo');
    const phoneField = document.getElementById('id_phone');
    const goalField = document.getElementById('id_referral_goal');

    // Setup nombre field
    if (nombreField) {
        const debouncedValidation = debounce(() => validateNombre(nombreField), 1500);

        nombreField.addEventListener('input', function() {
            const filtered = this.value.replace(/[^a-zA-ZaeiounuAEIOUNU\s'-]/g, '');
            this.value = filtered.slice(0, 60);
            debouncedValidation();
        });

        nombreField.addEventListener('blur', function() {
            if (this.value.trim() !== '') validateNombre(this);
        });
    }

    // Setup phone field
    if (phoneField) {
        const debouncedValidation = debounce(() => validatePhone(phoneField), 1500);

        phoneField.addEventListener('input', function() {
            filterNumericInput(this, 10);
            debouncedValidation();
        });

        phoneField.addEventListener('blur', function() {
            if (this.value.trim() !== '') validatePhone(this);
        });

        phoneField.addEventListener('keypress', function(e) {
            if (e.key < '0' || e.key > '9') e.preventDefault();
        });
    }

    // Setup goal field (numbers only, min 0)
    if (goalField) {
        goalField.addEventListener('input', function() {
            if (this.value < 0) this.value = 0;
        });
    }
})();
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Custom password change view | PasswordChangeView (built-in) | Django 1.4+ | Built-in handles session hash update, validation |
| Manual message display | messages framework + Bootstrap toasts | Modern pattern | Typed levels, auto-clear, consistent UX |
| UpdateView for profile | Function-based view with ModelForm | Both valid | FBV simpler for single-user editing with custom logic |
| jQuery for validation | Vanilla JS | 2015+ | No dependency, modern browsers support needed APIs |

**Deprecated/outdated:**
- `request.REQUEST` - Use `request.POST` or `request.GET` explicitly
- jQuery for simple DOM manipulation - vanilla JS preferred
- Custom password hashing - always use Django's built-in

## Open Questions

Things that couldn't be fully resolved:

1. **Toast Auto-Dismiss vs Manual Dismiss**
   - What we know: CONTEXT.md specifies "toast notification" for success
   - What's unclear: Whether toast should auto-dismiss or require click
   - Recommendation: Auto-dismiss after 3 seconds (matches home page pattern)

2. **Validation Timing for referral_goal**
   - What we know: Nombre and telefono use 1.5s debounce with input filtering
   - What's unclear: Whether referral_goal needs same validation UX
   - Recommendation: No debounce needed for number input, just min="0" constraint

3. **Error Display Priority**
   - What we know: Both inline errors and summary alert required
   - What's unclear: Whether to show all errors at once or highlight first
   - Recommendation: Show all inline errors + summary alert for non-field errors

## Sources

### Primary (HIGH confidence)
- [Django PasswordChangeView](https://docs.djangoproject.com/en/4.2/topics/auth/default/#django.contrib.auth.views.PasswordChangeView) - Built-in view attributes, session handling
- [Django ModelForm](https://docs.djangoproject.com/en/4.2/topics/forms/modelforms/) - ModelForm usage, fields, widgets
- [Django Messages Framework](https://docs.djangoproject.com/en/4.2/ref/contrib/messages/) - Adding/displaying messages, levels
- [Django Form Handling](https://docs.djangoproject.com/en/4.2/topics/forms/) - Form processing patterns

### Secondary (MEDIUM confidence)
- [Bootstrap 5 Forms](https://getbootstrap.com/docs/5.3/forms/overview/) - Form styling, validation states
- [Bootstrap 5 Toasts](https://getbootstrap.com/docs/5.3/components/toasts/) - Toast markup, JavaScript API
- Existing project patterns (register.html, home.html) - Validation, toast implementation

### Tertiary (LOW confidence)
- None - all findings verified with official sources or existing codebase

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using Django built-ins + existing Bootstrap setup
- Architecture: HIGH - Following established project patterns from register/home pages
- Pitfalls: HIGH - Based on official documentation and known Django behaviors

**Research date:** 2026-01-19
**Valid until:** 2026-04-19 (Django 4.2 LTS stable, patterns mature)
