# Phase 7: Referral Model & Registration - Research

**Researched:** 2026-01-19
**Domain:** Django Model Extensions, Self-Referential ForeignKey, Data Migrations, Query Parameter Handling
**Confidence:** HIGH

## Summary

This phase extends the existing `CustomUser` model with three new fields for referral tracking: a unique 8-character referral code, a self-referential ForeignKey for tracking who referred whom, and a configurable referral goal. The implementation uses Django's built-in `django.utils.crypto.get_random_string` for secure code generation, standard ForeignKey patterns for the self-referential relationship, and a three-step migration strategy to populate codes for existing users.

The registration view requires minor modification to capture the `?ref=CODE` query parameter from the URL and look up the referrer before saving the new user. This is straightforward Django view logic using `request.GET.get()` with graceful handling of invalid/missing codes.

**Primary recommendation:** Use Django's standard patterns - `get_random_string()` for codes, self-referential ForeignKey with `related_name='referrals'`, and a three-step migration (add nullable, populate, add unique constraint) for existing data.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Django | 4.2 LTS | Web framework | Already in use, provides all needed features |
| django.utils.crypto | (built-in) | Secure random string generation | Official Django utility, cryptographically secure |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| secrets (Python stdlib) | 3.14 | Underlying secure RNG | Used by Django's get_random_string internally |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| get_random_string | uuid.uuid4 | UUID is longer (36 chars), less user-friendly for sharing |
| get_random_string | secrets.token_urlsafe | More cryptographic, but produces non-alphanumeric chars |
| Self-referential FK | Separate Referral model | Adds complexity without benefit for simple parent tracking |

**Installation:**
```bash
# No new packages required - all features built into Django 4.2
```

## Architecture Patterns

### Recommended Project Structure
```
___/accounts/
    models.py              # Add referral fields to CustomUser
    views.py               # Modify register() to capture ref param
    forms.py               # No changes needed
    admin.py               # Add new fields to admin display
    migrations/
        0001_initial.py    # Existing
        0002_add_referral_fields.py    # New: Add nullable fields
        0003_populate_referral_codes.py # New: Data migration
        0004_referral_unique_constraint.py # New: Add unique constraint
```

### Pattern 1: Self-Referential ForeignKey for Referrals
**What:** A user can be referred by another user, creating a parent-child relationship.
**When to use:** When tracking "who referred whom" in a flat hierarchy (not multi-level).
**Example:**
```python
# Source: https://docs.djangoproject.com/en/4.2/ref/models/fields/#foreignkey
class CustomUser(AbstractUser):
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals',
        verbose_name='Referido por'
    )
```

**Key points:**
- `'self'` creates recursive relationship to same model
- `on_delete=SET_NULL` preserves referred users when referrer is deleted
- `null=True, blank=True` required for SET_NULL and optional relationship
- `related_name='referrals'` enables `user.referrals.all()` for reverse lookup

### Pattern 2: Secure Random Code Generation
**What:** Generate cryptographically secure alphanumeric codes for referral links.
**When to use:** When codes need to be unguessable and URL-safe.
**Example:**
```python
# Source: https://github.com/django/django/blob/main/django/utils/crypto.py
from django.utils.crypto import get_random_string

def generate_referral_code():
    """Generate an 8-character alphanumeric referral code."""
    # RANDOM_STRING_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return get_random_string(length=8)

# Usage in model field:
referral_code = models.CharField(
    max_length=8,
    unique=True,
    editable=False,
    verbose_name='Codigo de referido'
)
```

### Pattern 3: Three-Step Migration for Unique Field with Existing Data
**What:** Add a unique field to a model that already has rows in the database.
**When to use:** When adding `unique=True` fields to tables with existing data.
**Example:**
```python
# Migration 1: Add nullable field
migrations.AddField(
    model_name='customuser',
    name='referral_code',
    field=models.CharField(max_length=8, null=True),
)

# Migration 2: Populate values
def generate_codes(apps, schema_editor):
    from django.utils.crypto import get_random_string
    CustomUser = apps.get_model('accounts', 'CustomUser')
    for user in CustomUser.objects.all():
        while True:
            code = get_random_string(8)
            if not CustomUser.objects.filter(referral_code=code).exists():
                user.referral_code = code
                user.save(update_fields=['referral_code'])
                break

migrations.RunPython(generate_codes, migrations.RunPython.noop)

# Migration 3: Add unique constraint
migrations.AlterField(
    model_name='customuser',
    name='referral_code',
    field=models.CharField(max_length=8, unique=True, editable=False),
)
```

### Pattern 4: Query Parameter Capture in Views
**What:** Extract and validate URL query parameters in registration flow.
**When to use:** When capturing referral codes from links like `/register/?ref=ABC12345`.
**Example:**
```python
# Source: https://docs.djangoproject.com/en/4.2/ref/request-response/
def register(request):
    # Capture referral code from URL, default to None if missing/invalid
    ref_code = request.GET.get('ref', None)
    referrer = None

    if ref_code:
        try:
            referrer = CustomUser.objects.get(referral_code=ref_code)
        except CustomUser.DoesNotExist:
            # Invalid code - proceed without error (REG-03 requirement)
            pass

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.referred_by = referrer  # Set referrer (may be None)
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})
```

### Anti-Patterns to Avoid
- **Calling the function in default:** `default=get_random_string(8)` calls once at class definition, all users get same code. Use `default=generate_referral_code` (callable reference).
- **Direct model import in migrations:** Always use `apps.get_model()` for historical models in RunPython.
- **ForeignKey without null=True with SET_NULL:** Causes IntegrityError; SET_NULL requires null=True.
- **Trusting query params blindly:** Always use try/except or `.filter().first()` when looking up by user-supplied values.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Random string generation | Custom random.choice loop | `django.utils.crypto.get_random_string` | Cryptographically secure, tested |
| Unique code verification | Manual collision loop in model | DB-level unique constraint + save retry | Database handles atomicity |
| Query param extraction | Manual URL parsing | `request.GET.get('param', default)` | Built-in, handles encoding |
| Self-referential FK | Custom join table | ForeignKey('self', ...) | Standard Django pattern |

**Key insight:** Django 4.2 provides all required functionality out-of-the-box. No external packages are needed for this phase.

## Common Pitfalls

### Pitfall 1: Duplicate Referral Codes on Migration
**What goes wrong:** Running data migration generates same code for multiple users due to collision.
**Why it happens:** Random codes may collide, especially with short lengths and many users.
**How to avoid:** Use while loop with uniqueness check in migration:
```python
while True:
    code = get_random_string(8)
    if not CustomUser.objects.filter(referral_code=code).exists():
        break
```
**Warning signs:** IntegrityError during migration on unique constraint.

### Pitfall 2: get_random_string Called at Class Definition
**What goes wrong:** All users get identical referral code.
**Why it happens:** Using `default=get_random_string(8)` instead of `default=generate_referral_code`.
**How to avoid:** Pass callable reference, not function call result:
```python
# WRONG: default=get_random_string(8)
# RIGHT: default=generate_referral_code  # Note: no parentheses
```
**Warning signs:** All new users have same code, unique constraint violations.

### Pitfall 3: Missing null=True with SET_NULL
**What goes wrong:** Migration fails or runtime IntegrityError when deleting referrer.
**Why it happens:** SET_NULL tries to write NULL but field doesn't allow it.
**How to avoid:** Always pair `on_delete=SET_NULL` with `null=True, blank=True`.
**Warning signs:** IntegrityError mentioning NOT NULL constraint.

### Pitfall 4: Race Condition in Code Generation
**What goes wrong:** Two users created simultaneously get same code.
**Why it happens:** Check-then-insert without database transaction.
**How to avoid:** Use unique constraint at DB level + retry on IntegrityError:
```python
def save(self, *args, **kwargs):
    if not self.referral_code:
        for _ in range(10):  # Max retries
            self.referral_code = get_random_string(8)
            try:
                super().save(*args, **kwargs)
                return
            except IntegrityError:
                continue
        raise ValueError("Could not generate unique referral code")
    super().save(*args, **kwargs)
```
**Warning signs:** Occasional IntegrityError on user creation.

### Pitfall 5: Query Parameter Injection
**What goes wrong:** Malicious ref codes cause errors or information leakage.
**Why it happens:** Not handling DoesNotExist exception gracefully.
**How to avoid:** Use try/except or `.filter().first()` and never reveal whether code exists:
```python
# Safe pattern - returns None for invalid codes
referrer = CustomUser.objects.filter(referral_code=ref_code).first()
```
**Warning signs:** 500 errors when visiting `/register/?ref=INVALID`.

## Code Examples

Verified patterns from official sources:

### Complete Model Field Additions
```python
# Source: Django 4.2 documentation
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string


def generate_referral_code():
    """Generate unique 8-char alphanumeric code."""
    return get_random_string(length=8)


class CustomUser(AbstractUser):
    # ... existing fields ...

    # REF-01: Unique 8-char referral code
    referral_code = models.CharField(
        max_length=8,
        unique=True,
        editable=False,
        default=generate_referral_code,
        verbose_name='Codigo de referido'
    )

    # REF-02: Self-referential FK for referrer tracking
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals',
        verbose_name='Referido por'
    )

    # REF-03: Configurable referral goal
    referral_goal = models.PositiveIntegerField(
        default=10,
        verbose_name='Meta de referidos'
    )
```

### Data Migration for Existing Users (REF-04)
```python
# Source: https://docs.djangoproject.com/en/4.2/howto/writing-migrations/
from django.db import migrations


def generate_referral_codes(apps, schema_editor):
    """Generate unique referral codes for all existing users."""
    from django.utils.crypto import get_random_string

    CustomUser = apps.get_model('accounts', 'CustomUser')
    existing_codes = set()

    for user in CustomUser.objects.all():
        while True:
            code = get_random_string(8)
            if code not in existing_codes:
                existing_codes.add(code)
                user.referral_code = code
                user.save(update_fields=['referral_code'])
                break


def reverse_codes(apps, schema_editor):
    """Reverse migration - set all codes to None."""
    CustomUser = apps.get_model('accounts', 'CustomUser')
    CustomUser.objects.all().update(referral_code=None)


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_add_referral_fields'),
    ]

    operations = [
        migrations.RunPython(generate_referral_codes, reverse_codes),
    ]
```

### Updated Registration View (REG-01, REG-02, REG-03)
```python
# Source: Django view patterns
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from .models import CustomUser


def register(request):
    """User registration with referral code capture."""
    # REG-01: Capture ref parameter from URL
    ref_code = request.GET.get('ref')
    referrer = None

    # REG-02/REG-03: Look up referrer, gracefully handle invalid/missing
    if ref_code:
        referrer = CustomUser.objects.filter(referral_code=ref_code).first()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.referred_by = referrer  # May be None if invalid/missing
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})
```

### Updated Admin Configuration
```python
# Source: https://docs.djangoproject.com/en/4.2/ref/contrib/admin/
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + (
        'cedula', 'phone', 'referral_code', 'referred_by', 'referral_goal'
    )

    readonly_fields = ('referral_code',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('cedula', 'nombre_completo', 'phone', 'data_policy_accepted')
        }),
        ('Referral Info', {
            'fields': ('referral_code', 'referred_by', 'referral_goal')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('cedula', 'nombre_completo', 'phone', 'data_policy_accepted')
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| random.choice() | secrets.choice() | Python 3.6 | Cryptographically secure |
| default=func() | default=func | Always | Callable vs call result |
| Single migration | Three-step migration | Django 1.7+ | Handle unique fields on existing data |

**Deprecated/outdated:**
- `get_random_string()` without explicit length argument was deprecated, length is now required
- Using `random` module for security tokens (use `secrets` or Django's crypto)

## Open Questions

Things that couldn't be fully resolved:

1. **Referral Code Character Set**
   - What we know: Default is full alphanumeric (62 chars), 8 chars = ~47 bits entropy
   - What's unclear: Should we exclude confusing characters (0/O, 1/l/I)?
   - Recommendation: Use default chars; 8-char is sufficient for referral use case

2. **Code Generation in Model vs Form**
   - What we know: Can generate in model's save() or let DB default handle it
   - What's unclear: Best practice for when existing data needs population
   - Recommendation: Use model default for new users, RunPython migration for existing

## Sources

### Primary (HIGH confidence)
- [Django 4.2 ForeignKey Documentation](https://docs.djangoproject.com/en/4.2/ref/models/fields/#foreignkey) - Self-referential FK, SET_NULL behavior
- [Django Data Migrations Guide](https://docs.djangoproject.com/en/4.2/topics/migrations/#data-migrations) - RunPython, historical models
- [Django Crypto Source (GitHub)](https://github.com/django/django/blob/main/django/utils/crypto.py) - get_random_string implementation
- [Django Writing Migrations Howto](https://docs.djangoproject.com/en/4.2/howto/writing-migrations/) - Three-step unique field migration

### Secondary (MEDIUM confidence)
- [Django Admin Customization](https://docs.djangoproject.com/en/4.2/ref/contrib/admin/) - list_display, readonly_fields
- [Django ORM Cookbook - Self FK](https://books.agiliq.com/projects/django-orm-cookbook/en/latest/self_fk.html) - Self-referential patterns

### Tertiary (LOW confidence)
- Web search results on unique field migration patterns - Community patterns verified against official docs

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using only built-in Django features
- Architecture: HIGH - Following documented Django patterns
- Pitfalls: HIGH - Based on official documentation and verified community patterns

**Research date:** 2026-01-19
**Valid until:** 2026-04-19 (Django 4.2 LTS stable through April 2025+)
