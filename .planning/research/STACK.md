# Stack Research: v1.2 Referrals

**Project:** Django 4.2 Authentication Portal - Referral Tracking System
**Researched:** 2026-01-19
**Confidence:** HIGH

## Recommended Approach

**Use a self-referential ForeignKey on the existing CustomUser model** with a separate referral code field. No external packages needed.

### Why This Approach

| Criterion | Assessment | Rationale |
|-----------|------------|-----------|
| **Simplicity** | Excellent | 2-3 new fields on existing model, no new dependencies |
| **Data Integrity** | Strong | Django ForeignKey enforces referential integrity |
| **Query Performance** | Good | Single join to get referrer/referrals, `select_related` for optimization |
| **Migration** | Clean | Adds nullable fields, no data migration needed |
| **Maintenance** | Low | No external packages to update, standard Django patterns |

**Verdict:** For simple referrer-referred tracking without rewards/MLM complexity, self-referential FK is the optimal choice.

## Implementation Details

### Model Changes to CustomUser

Add these fields to the existing `CustomUser` model in `accounts/models.py`:

```python
from django.utils.crypto import get_random_string

class CustomUser(AbstractUser):
    # ... existing fields ...

    # Referral tracking
    referral_code = models.CharField(
        max_length=8,
        unique=True,
        blank=True,
        help_text='Unique referral code for this user'
    )
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals',
        help_text='User who referred this user'
    )
    referral_goal = models.PositiveIntegerField(
        default=10,
        help_text='Target number of referrals'
    )

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self._generate_unique_referral_code()
        super().save(*args, **kwargs)

    def _generate_unique_referral_code(self):
        """Generate a unique 8-character alphanumeric code"""
        while True:
            code = get_random_string(length=8, allowed_chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789')
            if not CustomUser.objects.filter(referral_code=code).exists():
                return code

    @property
    def referral_count(self):
        return self.referrals.count()

    @property
    def referral_progress(self):
        if self.referral_goal == 0:
            return 100
        return min(100, int((self.referral_count / self.referral_goal) * 100))
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **ForeignKey vs separate model** | ForeignKey on User | Simple 1:1 referrer relationship, no metadata needed |
| **on_delete** | SET_NULL | Preserve referral history if referrer account deleted |
| **related_name** | `referrals` | `user.referrals.all()` returns all users they referred |
| **Code length** | 8 characters | 2.8 trillion combinations, human-memorable, URL-safe |
| **Code charset** | Uppercase + digits (no 0,O,1,I,L) | Avoids ambiguous characters for readability |
| **Code generation timing** | On save() | Auto-generates for new users, backfill existing |

### Referral Code Strategy

**Use `django.utils.crypto.get_random_string`** - Django's built-in secure random string generator.

```python
from django.utils.crypto import get_random_string

# 8-char alphanumeric (no ambiguous chars)
code = get_random_string(length=8, allowed_chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789')
# Example output: "K7X3M9NP"
```

**Why not UUID?**
- UUIDs are 36 characters (`48a6ec8b-4929-426e-a1c3-9381b2e603d3`)
- Hard to type, share verbally, or remember
- 8-char code is sufficient for <1M users

**Why not sequential IDs?**
- Exposes user count (security concern)
- Allows enumeration attacks
- Looks unprofessional in URLs

### URL Parameter Handling

**Capture referral code via query parameter** in registration URL.

**Referral link format:**
```
https://yoursite.com/register/?ref=K7X3M9NP
```

**Registration view modification:**

```python
def register(request):
    referrer = None
    ref_code = request.GET.get('ref') or request.POST.get('ref_code')

    if ref_code:
        try:
            referrer = CustomUser.objects.get(referral_code=ref_code.upper())
        except CustomUser.DoesNotExist:
            pass  # Invalid code, continue without referrer

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.referred_by = referrer
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {
        'form': form,
        'referrer': referrer,
        'ref_code': ref_code,
    })
```

**Template (pass ref_code through form):**

```html
<form method="post">
    {% csrf_token %}
    {% if ref_code %}
    <input type="hidden" name="ref_code" value="{{ ref_code }}">
    {% endif %}
    {{ form.as_p }}
    <button type="submit">Registrarse</button>
</form>
```

### Querying Referrals

```python
# Get all users referred by current user
user.referrals.all()

# Get referral count
user.referrals.count()

# Get referrer of current user
user.referred_by

# Optimized query with referrer info (avoids N+1)
User.objects.select_related('referred_by').filter(...)

# Optimized query with referrals (for listing)
user = User.objects.prefetch_related('referrals').get(pk=user_id)
```

## Packages

### Recommendation: No External Packages

For this project's requirements (simple tracking, no rewards/MLM), external packages add complexity without benefit.

### Packages Evaluated and Rejected

| Package | Last Updated | Status | Why Not Use |
|---------|--------------|--------|-------------|
| **django-reflinks** | Nov 2023 | ARCHIVED | Repository archived, no longer maintained |
| **django-simple-referrals** | May 2018 | ABANDONED | Last release 6+ years ago, Django 2.0 only |
| **pinax-referrals** | June 2023 | Active but heavy | Complex (campaigns, responses, rewards), overkill for simple tracking |

**Key insight:** The referral package ecosystem is fragmented with many abandoned projects. Simple referral tracking is straightforward enough to implement with standard Django patterns.

### If Multi-Level Marketing Features Needed Later

**Only then consider:** `pinax-referrals` (4.3.0) - supports campaign-based referrals, response tracking, and multi-level structures.

```bash
# NOT RECOMMENDED for v1.2, but future reference:
pip install pinax-referrals==4.3.0
```

## Migration Strategy

### Migration File

```python
# accounts/migrations/XXXX_add_referral_fields.py

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),  # Adjust to last migration
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='referral_code',
            field=models.CharField(blank=True, max_length=8, unique=True, help_text='Unique referral code for this user'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='referred_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referrals', to='accounts.customuser', help_text='User who referred this user'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='referral_goal',
            field=models.PositiveIntegerField(default=10, help_text='Target number of referrals'),
        ),
    ]
```

### Backfilling Existing Users

After migration, generate codes for existing users:

```python
# Run in Django shell or management command
from accounts.models import CustomUser
from django.utils.crypto import get_random_string

def generate_unique_code():
    while True:
        code = get_random_string(length=8, allowed_chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789')
        if not CustomUser.objects.filter(referral_code=code).exists():
            return code

for user in CustomUser.objects.filter(referral_code=''):
    user.referral_code = generate_unique_code()
    user.save(update_fields=['referral_code'])
```

## Rejected Alternatives

### Alternative 1: Separate Referral Model

**What:** Create a `Referral` model linking two users

```python
class Referral(models.Model):
    referrer = models.ForeignKey(User, related_name='referrals_made')
    referred = models.ForeignKey(User, related_name='was_referred')
    created_at = models.DateTimeField(auto_now_add=True)
```

**Why Not:**
- Adds query complexity (join through intermediate table)
- Only needed if storing metadata (reward status, campaign, etc.)
- Project requirements don't include referral metadata
- Self-referential FK is simpler for 1:1 relationships

**When to use:** Multi-level marketing, referral rewards, campaign tracking.

### Alternative 2: UUID for Referral Codes

**What:** Use `uuid.uuid4()` as referral code

```python
referral_code = models.UUIDField(default=uuid.uuid4, unique=True)
```

**Why Not:**
- 36-character strings (`48a6ec8b-4929-426e-a1c3-9381b2e603d3`)
- Poor UX for sharing verbally or typing
- Overkill for <1M user scale
- Harder to include in SMS/social media sharing

**When to use:** Security-critical applications, API integrations, distributed systems.

### Alternative 3: URL Path-Based Referral Codes

**What:** Use URL path instead of query parameter

```
https://yoursite.com/r/K7X3M9NP/
```

**Why Not:**
- Requires additional URL routing
- Complicates registration flow (redirect needed)
- Query parameter (`?ref=X`) works seamlessly
- Less flexible for adding other parameters

**When to use:** Marketing campaigns where clean URLs matter.

### Alternative 4: Cookie-Based Referral Tracking

**What:** Store referral code in cookie, check on registration

**Why Not:**
- Adds complexity (middleware, cookie management)
- Privacy concerns (GDPR)
- Not needed for simple link sharing
- Cookies can be cleared before registration

**When to use:** Delayed conversion tracking, affiliate marketing.

## Technology Stack Summary

### Required (Already in Project)

| Technology | Version | Purpose |
|------------|---------|---------|
| Django | 4.2 LTS | Web framework |
| Python | 3.14 | Runtime |
| SQLite | - | Database |

### New Dependencies

**None.** All functionality uses Django built-ins:

- `django.utils.crypto.get_random_string` - Code generation
- `models.ForeignKey('self', ...)` - Self-referential relationship
- `request.GET.get('ref')` - URL parameter capture

### Files to Modify

| File | Changes |
|------|---------|
| `accounts/models.py` | Add 3 fields, save() override, properties |
| `accounts/views.py` | Capture ref parameter in register view |
| `accounts/migrations/XXXX_*.py` | New migration for fields |
| `templates/registration/register.html` | Hidden field for ref_code |
| `templates/home.html` | Display referral link, count, progress |

## Confidence Assessment

| Area | Confidence | Source | Notes |
|------|------------|--------|-------|
| Self-referential FK pattern | HIGH | Django ORM Cookbook, official docs | Standard Django pattern |
| get_random_string | HIGH | Django source code, Python docs | Built-in, cryptographically secure |
| Package recommendations | HIGH | PyPI, GitHub repos | Verified maintenance status |
| URL parameter approach | HIGH | Django docs, community patterns | Standard web pattern |
| Code length/charset | MEDIUM | Security best practices | 8 chars sufficient for scale |

## Sources

### Official Documentation
- [Django Models - Self-referential relationships](https://docs.djangoproject.com/en/4.2/topics/db/models/#recursive-relationships)
- [Django crypto module](https://docs.djangoproject.com/en/4.2/topics/signing/#module-django.utils.crypto)
- [Python secrets module](https://docs.python.org/3/library/secrets.html)

### Community Resources
- [Django ORM Cookbook - Self-referencing ForeignKey](https://books.agiliq.com/projects/django-orm-cookbook/en/latest/self_fk.html)
- [Understanding Django Self-Referential Foreign Keys](https://studygyaan.com/django/understanding-django-self-referential-foreign-keys)
- [Django Forum - Foreign key to self](https://forum.djangoproject.com/t/foreign-key-to-self/17227)

### Package Repositories
- [django-reflinks GitHub (ARCHIVED)](https://github.com/HearthSim/django-reflinks)
- [django-simple-referrals PyPI](https://pypi.org/project/django-simple-referrals/) - Last release May 2018
- [pinax-referrals GitHub](https://github.com/pinax/pinax-referrals)
- [Django Packages - Referrals Grid](https://djangopackages.org/grids/g/referrals/)

### Code Generation
- [Django get_random_string examples](https://www.programcreek.com/python/example/68244/django.utils.crypto.get_random_string)
- [Unique coupon code generation with Django](https://medium.com/@parker.cattell.atkins/unique-gift-coupon-code-generation-with-django-bf8f46ee3b9f)

## Summary

**Recommended Stack:** No new packages. Use Django built-ins only.

**Model approach:** Self-referential ForeignKey on CustomUser with `on_delete=SET_NULL`

**Code generation:** `django.utils.crypto.get_random_string` with 8-char alphanumeric codes

**URL handling:** Query parameter `?ref=CODE` captured in registration view

**Why:** Simple referral tracking (without rewards/MLM) is trivially implementable with standard Django patterns. External packages are either abandoned, overkill, or add unnecessary complexity for this use case.
