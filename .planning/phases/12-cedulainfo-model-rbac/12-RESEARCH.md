# Phase 12: CedulaInfo Model + RBAC - Research

**Researched:** 2026-01-19
**Domain:** Django model design, OneToOne relationships, admin read-only patterns
**Confidence:** HIGH

## Summary

This phase adds two related but distinct features: (1) a CedulaInfo model to store census/voting data fetched from Registraduria, and (2) a role field on CustomUser for USER/LEADER distinction. Both are straightforward Django model additions with well-documented patterns.

The CedulaInfo model uses a OneToOneField to link to CustomUser, with TextChoices for the 9 status options. The admin display follows Django's standard read-only pattern by overriding `has_add_permission`, `has_change_permission`, and `has_delete_permission` to return False. The role field uses TextChoices on CustomUser with a default of USER.

**Primary recommendation:** Add role field to existing CustomUser model via migration with default='USER'. Create CedulaInfo as new model in same accounts/models.py file. Use TextChoices for both status and role fields for type safety and IDE support.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Django | 4.2.x | Models, admin, migrations | Already in use in project |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| N/A | - | No additional dependencies | All features built into Django |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| TextChoices | Tuple choices | TextChoices provides type safety, IDE support, cleaner code |
| CharField for role | django-role-permissions | Overkill for 2-role system, adds dependency |
| TextField for raw_response | JSONField | JSONField has better query support but TextField is simpler for debug storage |

**Installation:**
```bash
# No additional packages needed - uses Django built-ins
```

## Architecture Patterns

### Recommended Project Structure
```
accounts/
    models.py          # Add CedulaInfo model, add role field to CustomUser
    admin.py           # Add CedulaInfoAdmin (read-only), update CustomUserAdmin
    migrations/
        0005_*.py      # Add role field to CustomUser (auto-generated)
        0006_*.py      # Create CedulaInfo model (auto-generated)
```

### Pattern 1: TextChoices for Status Field
**What:** Use Django's TextChoices enumeration for cleaner choice definition
**When to use:** Any CharField with predefined options
**Example:**
```python
# Source: https://docs.djangoproject.com/en/4.2/ref/models/fields/#choices

class CedulaInfo(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        PROCESSING = 'PROCESSING', 'Procesando'
        ACTIVE = 'ACTIVE', 'Activo'
        NOT_FOUND = 'NOT_FOUND', 'No encontrado'
        CANCELLED_DECEASED = 'CANCELLED_DECEASED', 'Cancelada - Fallecido'
        CANCELLED_OTHER = 'CANCELLED_OTHER', 'Cancelada - Otro'
        ERROR = 'ERROR', 'Error'
        TIMEOUT = 'TIMEOUT', 'Timeout'
        BLOCKED = 'BLOCKED', 'Bloqueado'

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
```

### Pattern 2: OneToOneField to Custom User
**What:** Create one-to-one relationship between CedulaInfo and CustomUser
**When to use:** When extending user data in a separate model
**Example:**
```python
# Source: https://docs.djangoproject.com/en/4.2/topics/auth/customizing/

from django.conf import settings

class CedulaInfo(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cedula_info',
        verbose_name='Usuario',
    )
```

### Pattern 3: Read-Only Admin Model
**What:** Prevent all modifications through admin interface
**When to use:** Data populated by external processes (scraping, API) that should not be manually edited
**Example:**
```python
# Source: https://docs.djangoproject.com/en/4.2/ref/contrib/admin/

from django.contrib import admin
from .models import CedulaInfo

@admin.register(CedulaInfo)
class CedulaInfoAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'status', 'departamento', 'municipio',
        'puesto', 'mesa', 'fetched_at'
    )
    list_filter = ('status', 'departamento')
    search_fields = ('user__cedula', 'user__nombre_completo', 'municipio')
    readonly_fields = [f.name for f in CedulaInfo._meta.get_fields()]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
```

### Pattern 4: Role Field with Default
**What:** Add role choices to existing CustomUser model
**When to use:** Simple role-based access control
**Example:**
```python
# Source: https://docs.djangoproject.com/en/4.2/ref/models/fields/#choices

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        USER = 'USER', 'Usuario'
        LEADER = 'LEADER', 'Lider'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Rol',
    )
```

### Anti-Patterns to Avoid
- **Putting CedulaInfo inline with UserAdmin:** Keep separate for clarity; CedulaInfo has many fields
- **Making raw_response editable:** This is debug data from scraping, should be read-only
- **Using IntegerChoices for status:** Text statuses are more readable in database queries
- **Hardcoding user model reference:** Always use `settings.AUTH_USER_MODEL` for ForeignKey/OneToOne

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Status choices | Dict or tuple list | TextChoices | Type safety, IDE autocomplete, get_FOO_display() |
| Role permissions | Custom middleware | Django's built-in permission checks | Battle-tested, integrates with admin |
| Read-only admin | Custom JavaScript to disable fields | has_X_permission() methods | Proper server-side enforcement |
| User extension | Modifying auth.models.User | OneToOneField to AUTH_USER_MODEL | Standard Django pattern |

**Key insight:** Django's admin permission system is designed for this exact use case. Overriding `has_add_permission`, `has_change_permission`, and `has_delete_permission` is the canonical way to create read-only admin views.

## Common Pitfalls

### Pitfall 1: Forgetting Default for Existing Users
**What goes wrong:** Migration fails or creates NULL values when adding role field
**Why it happens:** Existing users need a value for the new required field
**How to avoid:** Always specify `default=Role.USER` when adding role field
**Warning signs:** Migration prompts for default value or allows NULL

### Pitfall 2: Circular Import with AUTH_USER_MODEL
**What goes wrong:** ImportError when models reference each other
**Why it happens:** Importing CustomUser directly instead of using settings reference
**How to avoid:** Use `settings.AUTH_USER_MODEL` for ForeignKey/OneToOne to user
**Warning signs:** "cannot import name 'CustomUser'" errors

### Pitfall 3: Incomplete readonly_fields
**What goes wrong:** Some fields are still editable in admin detail view
**Why it happens:** readonly_fields only applies to explicitly listed fields
**How to avoid:** Dynamically get all fields: `[f.name for f in Model._meta.get_fields()]`
**Warning signs:** Fields appear with input widgets in admin

### Pitfall 4: Missing Verbose Names in Spanish
**What goes wrong:** Admin displays English field names to Spanish-speaking users
**Why it happens:** Forgetting to set verbose_name on fields
**How to avoid:** Add Spanish verbose_name to all user-facing fields
**Warning signs:** Mix of English and Spanish in admin interface

### Pitfall 5: Not Handling CedulaInfo Absence
**What goes wrong:** AttributeError when accessing user.cedula_info before data fetched
**Why it happens:** CedulaInfo created lazily by background task, not on user registration
**How to avoid:** Use hasattr() or try/except when accessing cedula_info
**Warning signs:** 500 errors on user profile before scraping completes

## Code Examples

Verified patterns from official sources:

### Complete CedulaInfo Model
```python
# accounts/models.py
# Source: https://docs.djangoproject.com/en/4.2/ref/models/fields/

from django.conf import settings
from django.db import models


class CedulaInfo(models.Model):
    """Census/voting information fetched from Registraduria."""

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        PROCESSING = 'PROCESSING', 'Procesando'
        ACTIVE = 'ACTIVE', 'Activo'
        NOT_FOUND = 'NOT_FOUND', 'No encontrado'
        CANCELLED_DECEASED = 'CANCELLED_DECEASED', 'Cancelada - Fallecido'
        CANCELLED_OTHER = 'CANCELLED_OTHER', 'Cancelada - Otro'
        ERROR = 'ERROR', 'Error'
        TIMEOUT = 'TIMEOUT', 'Timeout'
        BLOCKED = 'BLOCKED', 'Bloqueado'

    # Link to user
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cedula_info',
        verbose_name='Usuario',
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado',
    )

    # Voting location fields
    departamento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Departamento',
    )
    municipio = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Municipio',
    )
    puesto = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Puesto de votacion',
    )
    direccion = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Direccion',
    )
    mesa = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Mesa',
    )

    # Cancelled cedula fields
    novedad = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Novedad',
    )
    resolucion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Resolucion',
    )
    fecha_novedad = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Fecha de novedad',
    )

    # Metadata
    fetched_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de consulta',
    )
    error_message = models.TextField(
        blank=True,
        verbose_name='Mensaje de error',
    )
    raw_response = models.TextField(
        blank=True,
        verbose_name='Respuesta cruda',
        help_text='HTML/JSON response from Registraduria for debugging',
    )

    class Meta:
        verbose_name = 'Informacion de cedula'
        verbose_name_plural = 'Informacion de cedulas'

    def __str__(self):
        return f"{self.user.cedula} - {self.get_status_display()}"
```

### Role Field Addition to CustomUser
```python
# accounts/models.py - add to existing CustomUser class
# Source: https://docs.djangoproject.com/en/4.2/ref/models/fields/#choices

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        USER = 'USER', 'Usuario'
        LEADER = 'LEADER', 'Lider'

    # ... existing fields ...

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Rol',
    )
```

### Complete CedulaInfoAdmin
```python
# accounts/admin.py
# Source: https://docs.djangoproject.com/en/4.2/ref/contrib/admin/

from django.contrib import admin
from .models import CedulaInfo


@admin.register(CedulaInfo)
class CedulaInfoAdmin(admin.ModelAdmin):
    """Read-only admin for CedulaInfo - data comes from scraping only."""

    list_display = (
        'user',
        'status',
        'departamento',
        'municipio',
        'puesto',
        'direccion',
        'mesa',
        'novedad',
        'resolucion',
        'fecha_novedad',
        'fetched_at',
        'error_message',
    )
    list_filter = ('status', 'departamento')
    search_fields = (
        'user__cedula',
        'user__nombre_completo',
        'municipio',
        'puesto',
    )
    ordering = ('-fetched_at',)

    # Make all fields read-only
    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    # Prevent add/change/delete
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
```

### Updated CustomUserAdmin with Role
```python
# accounts/admin.py - update existing CustomUserAdmin
# Source: https://docs.djangoproject.com/en/4.2/ref/contrib/admin/

class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + (
        'cedula', 'phone', 'referral_code', 'referred_by', 'referral_goal', 'role'
    )

    readonly_fields = ('referral_code',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('cedula', 'nombre_completo', 'phone', 'data_policy_accepted')
        }),
        ('Referral Info', {
            'fields': ('referral_code', 'referred_by', 'referral_goal')
        }),
        ('Role', {
            'fields': ('role',),
            'description': 'Solo superadmins pueden cambiar roles',
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('cedula', 'nombre_completo', 'phone', 'data_policy_accepted')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """Make role read-only for non-superusers."""
        readonly = list(self.readonly_fields)
        if not request.user.is_superuser:
            readonly.append('role')
        return readonly
```

## Migration Strategy

### For Role Field (existing model)
```bash
# After adding role field to CustomUser model
python manage.py makemigrations accounts --name add_role_field
python manage.py migrate
```

The migration will include `default=CustomUser.Role.USER` ensuring existing users get the USER role.

### For CedulaInfo Model (new model)
```bash
# After adding CedulaInfo model
python manage.py makemigrations accounts --name create_cedula_info
python manage.py migrate
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Tuple choices | TextChoices/IntegerChoices | Django 3.0 | Cleaner code, type safety |
| has_change_permission only | has_add + has_change + has_delete | Always | Complete read-only control |
| User.objects.get() | get_user_model() or settings.AUTH_USER_MODEL | Django 1.5 | Custom user model support |

**Deprecated/outdated:**
- Tuple-based choices: Still work but TextChoices is preferred for new code
- Direct User import: Always use settings.AUTH_USER_MODEL for foreign keys

## Open Questions

Things that couldn't be fully resolved:

1. **Raw Response Storage Format**
   - What we know: TextField can store any string (HTML or JSON)
   - What's unclear: Whether JSONField would be better for structured queries
   - Recommendation: Use TextField since raw_response is for debugging, not querying

2. **CedulaInfo Creation Timing**
   - What we know: Created by background task after scraping
   - What's unclear: Whether to create PENDING record at registration or wait for first scrape
   - Recommendation: Create lazily on first scrape - simpler, no empty records

## Sources

### Primary (HIGH confidence)
- [Django Admin Reference](https://docs.djangoproject.com/en/4.2/ref/contrib/admin/) - has_X_permission methods, readonly_fields
- [Django Model Fields Reference](https://docs.djangoproject.com/en/4.2/ref/models/fields/) - CharField, choices, TextChoices
- [Django Topics: Customizing Auth](https://docs.djangoproject.com/en/4.2/topics/auth/customizing/) - OneToOneField pattern, AUTH_USER_MODEL

### Secondary (MEDIUM confidence)
- Existing project code (accounts/models.py, accounts/admin.py) - Verified patterns already in use

### Tertiary (LOW confidence)
- N/A - All findings verified with primary sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Uses only Django built-ins already in project
- Architecture: HIGH - Official Django documentation patterns
- Pitfalls: HIGH - Common issues documented in Django docs and verified in codebase
- Code examples: HIGH - Adapted from official Django documentation

**Research date:** 2026-01-19
**Valid until:** 90 days (stable Django patterns, no external dependencies)
