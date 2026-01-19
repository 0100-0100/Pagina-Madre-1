# Research Summary: v1.2 Referrals

**Project:** ___ (Django Authentication Portal)
**Milestone:** v1.2 Referrals
**Research Date:** 2026-01-19
**Confidence:** HIGH

## Executive Summary

Referral tracking for this Django app is straightforward with standard patterns. **No external packages needed** — use a self-referential ForeignKey on CustomUser with 3 new fields. The main complexity is in the registration flow (capturing referral codes) and ensuring proper migration handling.

**Key insight:** Use `on_delete=SET_NULL` (not CASCADE) to prevent deleting referred users when a referrer is deleted.

## Stack Decision

**Use Django built-ins only:**

- `models.ForeignKey('self', on_delete=SET_NULL)` — referrer relationship
- `django.utils.crypto.get_random_string` — 8-char referral code generation
- `request.GET.get('ref')` — URL parameter capture

**No pip packages needed.** Existing referral packages (django-reflinks, django-simple-referrals, pinax-referrals) are either abandoned, archived, or overkill for simple tracking.

**Model additions to CustomUser:**
```python
referral_code = CharField(max_length=8, unique=True)  # Auto-generated
referred_by = ForeignKey('self', on_delete=SET_NULL, null=True, related_name='referrals')
referral_goal = PositiveIntegerField(default=10)
```

## Feature Requirements

**Table Stakes (must have):**

| Feature | Complexity | Notes |
|---------|------------|-------|
| Referral link per user | Low | 8-char code, auto-generated |
| Registration captures referrer | Low | `?ref=CODE` URL param |
| Home: referral count | Low | `user.referrals.count()` |
| Home: progress toward goal | Low | Bootstrap progress bar |
| Home: shareable link | Low | Copy-to-clipboard button |
| Profile: edit nombre, telefono | Low | Simple ModelForm |
| Profile: change password | Medium | Django PasswordChangeForm |
| Profile: set referral goal | Low | Integer field |
| Referidos: table with 4 columns | Low | Bootstrap table |
| Navigation links | Low | Navbar update |

**Nice-to-haves (if time):**
- Copy-to-clipboard with feedback toast
- Empty state messaging ("No tienes referidos aún")
- Table zebra striping (`.table-striped`)

**Anti-features (avoid):**
- Multi-level referral tracking (MLM complexity)
- Referral rewards/incentives (out of scope)
- Self-referral prevention logic (overkill for <100 users)
- Referral analytics dashboard (overengineering)

## Architecture Pattern

**Model design:** Extend CustomUser (not separate model)
- Simple 1:1 referrer relationship
- Data always accessed together

**URL structure:**
- `/register/?ref=CODE` — modified to capture referrer
- `/profile/` — new page for editing
- `/referidos/` — new page with table

**Template structure:**
- Extract navbar to `includes/navbar.html` for reuse
- Create `profile.html` and `referidos.html`
- Update `home.html` with referral stats

## Critical Pitfalls

| Pitfall | Prevention |
|---------|------------|
| CASCADE deletes referred users | Use `on_delete=SET_NULL` |
| Migration fails on existing users | Add field with `null=True` |
| Existing users have no codes | Data migration to backfill |
| Self-referral fraud | Check cedula match (optional) |
| Division by zero on goal | Handle goal=0 in template |

## Implications for Roadmap

**Suggested phase structure:**

### Phase 7: Referral Model Foundation
- Add 3 fields to CustomUser
- Create migration
- Backfill referral codes for existing users
- Update registration to capture `?ref=` param

### Phase 8: Home Page Referral UI
- Display referral count and progress bar
- Show shareable referral link with copy button
- Add navigation links to new pages

### Phase 9: Profile Page
- Create ProfileForm for nombre, telefono, goal
- Add password change section (Django built-in)
- Extract navbar to include

### Phase 10: Referidos Page
- Create table with 4 columns
- Empty state handling
- Pagination (if needed)

**Phase ordering rationale:**
- Model first — all other features depend on it
- Home page — users see value immediately
- Profile — enables goal setting
- Referidos — completes feature set

## Estimated Effort

| Phase | Estimate |
|-------|----------|
| Phase 7: Model Foundation | 1-2 hours |
| Phase 8: Home Referral UI | 1-2 hours |
| Phase 9: Profile Page | 2-3 hours |
| Phase 10: Referidos Page | 1-2 hours |
| **Total** | **5-9 hours** |

## Open Questions

1. **Password change:** Use Django's built-in PasswordChangeView or custom form?
   - Recommendation: Django built-in (proven, secure)

2. **Referral goal time period:** All-time count or monthly?
   - User requirement says "total count" — use all-time

## Sources

- Django ORM Cookbook (self-referential FK patterns)
- Django official documentation (ForeignKey, get_random_string)
- Bootstrap 5 documentation (progress bars, tables)
- OWASP (URL parameter security)

---

*Research complete. Ready for `/gsd:define-requirements` or roadmap creation.*
