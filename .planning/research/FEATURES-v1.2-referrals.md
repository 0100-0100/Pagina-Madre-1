# Features Research: v1.2 Referrals

**Domain:** Referral tracking system for Django authentication portal
**Researched:** 2026-01-19
**Confidence:** HIGH (based on user requirements + industry patterns)

## Table Stakes

Features the user explicitly requested. Missing = milestone incomplete.

| Feature | Why Required | Complexity | Implementation Notes |
|---------|--------------|------------|---------------------|
| **Unique referral link per user** | User requirement: "Referral link per user (embedded in registration URL)" | Low | Generate short code on user creation, store on User model |
| **Referrer capture on registration** | User requirement: "Registration captures referrer from URL parameter" | Low | Read `?ref=CODE` param, store in session, link on user creation |
| **Referrer-referred relationship** | User requirement: "Track referrer-referred relationships" | Low | ForeignKey from User to User (self-referential) or separate model |
| **Home: referral count display** | User requirement: "Home page: referral count" | Low | Simple `user.referrals.count()` query |
| **Home: progress toward goal** | User requirement: "progress toward goal" | Medium | Visual progress bar (Bootstrap), requires goal field on User |
| **Home: shareable referral link** | User requirement: "shareable link" | Low | Display link with copy-to-clipboard button |
| **Profile: edit nombre** | User requirement: "Profile page: edit nombre" | Low | Form with nombre_completo field |
| **Profile: edit telefono** | User requirement: "Profile page: edit telefono" | Low | Form with phone field |
| **Profile: change password** | User requirement: "Profile page: edit password" | Medium | Use Django's PasswordChangeView, separate from profile form |
| **Profile: set referral goal** | User requirement: "set referral goal" | Low | Integer field on User model, form input |
| **Referidos page: table display** | User requirement: "table of referred users" | Medium | Bootstrap table with requested columns |
| **Referidos: Nombre column** | User requirement explicit column | Low | Display referred user's nombre_completo |
| **Referidos: Cedula column** | User requirement explicit column | Low | Display referred user's cedula |
| **Referidos: Telefono column** | User requirement explicit column | Low | Display referred user's phone |
| **Referidos: Fecha de registro column** | User requirement explicit column | Low | Display referred user's date_joined |
| **Navigation to new pages** | User requirement: "Navigation from home to new pages" | Low | Add navbar links to Perfil and Referidos |

### Table Stakes Summary

The user's requirements are straightforward and well-scoped:
- **Flat referral structure** (one level only, no MLM/pyramid)
- **Tracking only** (no rewards/incentives - explicitly out of scope per PROJECT.md)
- **Three pages** (enhanced Home + new Profile + new Referidos)
- **Basic CRUD** for profile fields

---

## Nice-to-Haves

Enhancements that improve UX but are not required for milestone completion.

| Feature | Value Proposition | Complexity | When to Consider |
|---------|-------------------|------------|------------------|
| **Copy-to-clipboard with feedback** | Better UX for sharing link | Low | Add if time permits; simple JS |
| **Progress bar animation** | More engaging goal visualization | Low | CSS animation on Bootstrap progress bar |
| **Empty state messaging** | Better UX when 0 referrals | Low | "Comparte tu enlace para empezar" message |
| **Referidos table sorting** | Let users sort by date, name | Medium | Bootstrap + JS or django-tables2 |
| **Referidos table search/filter** | Find specific referrals | Medium | Client-side JS filter for small scale |
| **Profile form validation feedback** | Real-time validation like auth forms | Medium | Consistent with v1.1 patterns |
| **Referral link QR code** | Alternative sharing method | Low | Python qrcode library, generate on demand |
| **Milestone celebrations** | Toast/modal when reaching goal | Low | JS check on page load |
| **Referral statistics** | Referrals this week/month | Low | Simple date filtering on queryset |
| **Zebra striping on table** | Better readability | Low | Bootstrap `.table-striped` class |
| **Sticky table header** | Keep column names visible when scrolling | Low | CSS `position: sticky` |
| **Responsive table** | Horizontal scroll on mobile | Low | Bootstrap `.table-responsive` wrapper |

### Nice-to-Have Recommendations

**Prioritize (high impact, low effort):**
1. Copy-to-clipboard with feedback
2. Empty state messaging
3. Zebra striping on table
4. Responsive table wrapper

**Defer (overkill for scale):**
- Table sorting/filtering (unnecessary for <100 users)
- QR codes (adds dependency, questionable value)
- Milestone celebrations (scope creep)

---

## Anti-Features

Features to deliberately NOT build. Common mistakes in referral systems.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Multi-level referral tracking** | Adds complexity, not requested, smells like MLM | Flat structure: user -> referrer, one level only |
| **Referral rewards/incentives** | Explicitly out of scope per PROJECT.md; adds fraud risk | Goal tracking only, no monetary/point rewards |
| **Self-referral prevention logic** | Overengineering for <100 users; adds complexity | Accept risk; can manually review if needed |
| **Sophisticated fraud detection** | Overkill for small scale, adds complexity | Trust users; manual review via Django admin |
| **Referral link expiration** | Adds complexity, not requested | Links valid indefinitely |
| **Attribution cookies/tracking** | Not needed for simple URL param approach | Session-based: capture ref param, use on registration |
| **Referral leaderboards** | Not requested, adds competitive dynamics | Private goal progress only |
| **Social sharing integrations** | Adds external dependencies, not requested | Simple copy-to-clipboard link |
| **Referral email notifications** | Requires email infrastructure not in project | Manual checking of referral count |
| **Partial cedula masking in table** | Security theater; all users authenticated anyway | Show full cedula as requested |
| **Editable cedula on profile** | Cedula is identity, should not change | Display-only on profile, cedula locked |
| **Username/email profile editing** | Not requested; cedula is username | Keep out of scope |
| **Tiered reward systems** | Not requested; goal is tracking only | Simple numeric goal, no tiers |
| **Referral analytics dashboard** | Overengineering for simple tracking | Basic count and progress bar sufficient |
| **A/B testing referral messaging** | Enterprise feature, not requested | Single shareable link |
| **Mobile app deep links** | No mobile app exists | Standard web URL only |

### Critical Anti-Feature: Avoid Complexity Creep

The user's requirements are intentionally simple:
- Track who referred whom
- Show progress toward a personal goal
- Display a table of referrals

**Do NOT add:**
- Tiered rewards ("refer 5 people, get X")
- Referral analytics dashboards
- A/B testing of referral messaging
- Viral loop optimization
- Gamification elements (badges, levels)

These are standard in commercial referral platforms but are explicitly out of scope for this tracking-only system.

---

## Feature Dependencies

```
User Model Changes
    |
    +-- referral_code (CharField, unique)
    |       |
    |       +-> Home: shareable link display
    |       +-> Registration: URL param capture
    |
    +-- referred_by (ForeignKey to User, nullable)
    |       |
    |       +-> Home: referral count query
    |       +-> Referidos: table data source
    |
    +-- referral_goal (PositiveIntegerField, default=10)
            |
            +-> Home: progress bar calculation
            +-> Profile: goal editing

Registration Flow Change
    |
    +-- Capture ?ref= param from URL
    +-- Store in session (persist through form validation)
    +-- On user creation, lookup referrer by code
    +-- Set referred_by on new user

New Pages
    |
    +-- Profile page (perfil.html)
    |       +-- ProfileForm (nombre_completo, phone)
    |       +-- Link to password change (separate page)
    |       +-- ReferralGoalForm (referral_goal)
    |
    +-- Referidos page (referidos.html)
            +-- Table of User.objects.filter(referred_by=request.user)

Navigation Enhancement
    |
    +-- Navbar links in base.html or home.html
            +-- Link to /perfil/
            +-- Link to /referidos/
```

---

## Referral Link Format Decision

**Options considered:**

| Format | Example | Pros | Cons |
|--------|---------|------|------|
| UUID | `?ref=a1b2c3d4-e5f6-...` | Unpredictable, secure | Long (36 chars), hard to share verbally |
| Short alphanumeric | `?ref=X7K2M9PQ` | Shorter, shareable | Small collision risk (manageable) |
| Cedula-based | `?ref=1234567890` | No new field needed | Exposes PII in URL |
| User ID | `?ref=42` | Simple | Enumerable, predictable |

**Recommendation:** Short alphanumeric code (8 characters)
- Example: `https://example.com/register/?ref=X7K2M9PQ`
- Generated on user creation using `secrets.token_urlsafe(6)` (produces 8 chars)
- Stored in `referral_code` field on User model
- Unpredictable, short enough to share, no PII exposure

**Implementation:**
```python
import secrets

def generate_referral_code():
    return secrets.token_urlsafe(6)  # 8 characters
```

---

## Referidos Table Design

Based on UX best practices and user requirements:

| Column | Alignment | Purpose | Notes |
|--------|-----------|---------|-------|
| Nombre | Left | Human identifier (most important) | First column per UX guidelines |
| Cedula | Left | Secondary identifier | User-requested |
| Telefono | Left | Contact info | User-requested |
| Fecha de registro | Left | When they joined | Format as DD/MM/YYYY for Colombia |

**Bootstrap implementation:**
```html
<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>Nombre</th>
        <th>Cedula</th>
        <th>Telefono</th>
        <th>Fecha de registro</th>
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
      {% empty %}
      <tr>
        <td colspan="4" class="text-center text-muted">
          No tienes referidos aun. Comparte tu enlace para empezar.
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
```

**Deliberately omit:**
- Row actions (no edit/delete needed)
- Sorting controls (overkill for small dataset)
- Search/filter (overkill for small dataset)
- Pagination (unnecessary for <100 referrals per user)

---

## Profile Page Design

Based on Django best practices and user requirements:

**Two separate concerns:**
1. Profile editing (nombre, telefono, referral goal)
2. Password change (uses Django's built-in view)

**Recommendation:** Single profile page with link to password change

```
/perfil/                  - Profile edit form
/perfil/cambiar-password/ - Django PasswordChangeView
```

**Profile form fields:**
| Field | Type | Editable | Notes |
|-------|------|----------|-------|
| Cedula | Display only | No | Identity, cannot change |
| Nombre Completo | Text input | Yes | User requirement |
| Telefono | Text input | Yes | User requirement |
| Meta de Referidos | Number input | Yes | User requirement |
| Password | Link | N/A | Links to separate page |

**Django implementation approach:**
- Use Django's PasswordChangeView (proven, secure)
- Custom template for Spanish labels
- Redirect to profile with success message after change

---

## Progress Bar Design

User requirement: "progress toward goal"

**Bootstrap progress bar:**
```html
<div class="mb-3">
  <div class="d-flex justify-content-between mb-1">
    <span>Progreso hacia tu meta</span>
    <span>{{ referral_count }}/{{ referral_goal }}</span>
  </div>
  <div class="progress">
    <div class="progress-bar"
         role="progressbar"
         style="width: {{ progress_percent }}%"
         aria-valuenow="{{ referral_count }}"
         aria-valuemin="0"
         aria-valuemax="{{ referral_goal }}">
    </div>
  </div>
</div>
```

**Progress calculation:**
```python
progress_percent = min(100, (referral_count / referral_goal) * 100)
```

**Edge cases:**
- Goal = 0: Show 100% (or hide progress bar)
- Count > Goal: Cap at 100%
- No goal set: Default to 10

---

## MVP Feature Set

For v1.2 MVP, implement all Table Stakes features. The user's requirements are already well-scoped.

**Phase order recommendation:**

1. **Model changes first** - Add fields to CustomUser (referral_code, referred_by, referral_goal)
2. **Registration flow** - Capture referral param, link users
3. **Home page enhancements** - Count, progress bar, shareable link
4. **Profile page** - New page with profile form + goal form + password link
5. **Referidos page** - New page with table
6. **Navigation** - Add links to navbar

This order ensures each feature builds on the previous, with working functionality at each step.

---

## Complexity Assessment

| Feature | Complexity | Time Estimate | Dependencies |
|---------|------------|---------------|--------------|
| Model changes (3 fields) | Low | 30 min | Migration |
| Referral code generation | Low | 15 min | secrets module |
| Registration flow change | Low | 1 hour | Session handling |
| Home: referral count | Low | 15 min | Query |
| Home: progress bar | Low | 30 min | Bootstrap |
| Home: shareable link | Low | 30 min | URL building |
| Copy-to-clipboard | Low | 30 min | JavaScript |
| Profile page view | Medium | 1 hour | New view + template |
| Profile form | Low | 30 min | ModelForm |
| Password change | Low | 30 min | Django built-in |
| Referidos page view | Low | 30 min | New view + template |
| Referidos table | Low | 30 min | Bootstrap table |
| Navigation links | Low | 15 min | Navbar update |

**Total MVP Estimate:** 6-8 hours for all table stakes features

---

## Sources

### Referral System Best Practices
- [Viral Loops - Referral Program Best Practices 2025](https://viral-loops.com/blog/referral-program-best-practices-in-2025/)
- [Prefinery - Key Referral Program Metrics](https://www.prefinery.com/blog/10-key-referral-program-metrics-to-track-2025/)
- [Impact - Referral Tracking Guide](https://impact.com/referral/referral-tracking/)
- [Cello - Ultimate Guide to Referral Tracking](https://cello.so/the-ultimate-guide-to-referral-tracking/)

### Django Implementation Patterns
- [Django Packages - Referrals Grid](https://djangopackages.org/grids/g/referrals/)
- [django-simple-referrals Documentation](https://django-simple-referrals.readthedocs.io/en/latest/readme.html)
- [HearthSim django-reflinks](https://github.com/HearthSim/django-reflinks)
- [pinax-referrals](https://github.com/pinax/pinax-referrals)

### Table UI Best Practices
- [Pencil & Paper - Data Table UX Patterns](https://www.pencilandpaper.io/articles/ux-pattern-analysis-enterprise-data-tables)
- [Nielsen Norman Group - Data Tables](https://www.nngroup.com/articles/data-tables/)
- [MobileSpoon - Table Design 20 Rules](https://www.mobilespoon.net/2019/11/design-ui-tables-20-rules-guide.html)
- [DronaHQ - Table UI Design Best Practices](https://www.dronahq.com/table-ui-design/)

### Profile/Password Management
- [Django Documentation - Authentication](https://docs.djangoproject.com/en/4.0/topics/auth/default/)
- [LearnDjango - Password Change Tutorial](https://learndjango.com/tutorials/django-login-and-logout-tutorial)
- [Django Documentation - Password Management](https://docs.djangoproject.com/en/6.0/topics/auth/passwords/)

### Anti-Patterns and Fraud Prevention
- [Voucherify - Combat Referral Abuse](https://www.voucherify.io/blog/blowing-the-whistle-how-to-combat-referral-abuse-and-fraud)
- [Viral Loops - Referral Marketing Risks](https://viral-loops.com/blog/referral-marketing-risks-and-challenges/)
- [Nector - Referral Program Mistakes](https://www.nector.io/blog/5-common-referral-program-mistakes-and-the-best-apps-to-fix-them)

### Gamification & Progress Display
- [GrowSurf - Gamification in Referral Marketing](https://growsurf.com/blog/gamification-in-referral-marketing)
- [Comarch - Progress Bars for Engagement](https://www.comarch.com/trade-and-services/loyalty-marketing/blog/use-gamification-progress-bars-to-drive-customer-engagement/)
- [SaaSquatch - Gamification for Referral Programs](https://www.saasquatch.com/blog/how-to-use-gamification-for-referral-and-loyalty-programs)

### Referral Code Formats
- [GrowSurf - Referral Code Examples](https://growsurf.com/blog/referral-code-examples)
- [Medium - Referral Code Generation Architecture](https://medium.com/@siddhusingh/referral-code-generation-architecture-contention-free-scalable-approach-68ea44ee5fb0)

---

## Confidence Assessment

**Overall Confidence:** HIGH

| Area | Confidence | Reason |
|------|------------|--------|
| Table Stakes | HIGH | Directly from user requirements in PROJECT.md |
| Model Design | HIGH | Standard Django patterns, verified with existing libraries |
| UI Patterns | HIGH | Bootstrap 5 official components, proven patterns |
| Password Change | HIGH | Django built-in PasswordChangeView |
| Anti-Features | HIGH | Explicitly documented in PROJECT.md (out of scope) |

**No low-confidence items.** All features map directly to user requirements, and implementation patterns are well-established in Django/Bootstrap ecosystem.
