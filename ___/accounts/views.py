from datetime import timedelta

from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django_q.tasks import async_task

from .decorators import leader_or_self_required
from .forms import CustomUserCreationForm, ProfileForm, CustomPasswordChangeForm
from .models import CedulaInfo, CustomUser


def register(request):
    """User registration view with referral code capture."""
    # REG-01: Capture ref parameter from URL
    ref_code = request.GET.get('ref')
    referrer = None

    # REG-02/REG-03: Look up referrer, gracefully handle invalid/missing
    if ref_code:
        from .models import CustomUser
        referrer = CustomUser.objects.filter(referral_code=ref_code).first()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.referred_by = referrer  # May be None if invalid/missing code
            user.save()
            login(request, user)
            try:
                return redirect('home')
            except:
                return redirect('/admin/')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def home(request):
    """Home page view with referral statistics."""
    referral_count = request.user.referrals.count()
    referral_goal = request.user.referral_goal
    progress_percent = min(100, int((referral_count / referral_goal) * 100)) if referral_goal > 0 else 100
    referral_url = request.build_absolute_uri(reverse('register') + f'?ref={request.user.referral_code}')

    return render(request, 'home.html', {
        'user': request.user,
        'referral_count': referral_count,
        'referral_goal': referral_goal,
        'progress_percent': progress_percent,
        'referral_url': referral_url,
    })


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
            messages.error(request, 'Por favor corrige los errores')
    else:
        form = ProfileForm(instance=request.user)

    # Get census information for profile display
    cedula_info = getattr(request.user, 'cedula_info', None)
    is_polling = False
    if cedula_info:
        is_polling = cedula_info.status in [
            CedulaInfo.Status.PENDING,
            CedulaInfo.Status.PROCESSING
        ]

    return render(request, 'profile.html', {
        'form': form,
        'user': request.user,
        'cedula_info': cedula_info,
        'is_polling': is_polling,
        'is_leader': request.user.role == CustomUser.Role.LEADER,
        'show_refresh': True,  # On own profile, always show if leader
    })


@login_required
def census_section_view(request):
    """Return census section partial for HTMX polling."""
    cedula_info = getattr(request.user, 'cedula_info', None)

    # Determine if polling should continue
    is_polling = False
    if cedula_info:
        is_polling = cedula_info.status in [
            CedulaInfo.Status.PENDING,
            CedulaInfo.Status.PROCESSING
        ]

    return render(request, 'partials/_census_section.html', {
        'cedula_info': cedula_info,
        'is_polling': is_polling,
        'user': request.user,
        'is_leader': request.user.role == CustomUser.Role.LEADER,
        'show_refresh': True,
    })


@login_required
@leader_or_self_required
def refresh_cedula_view(request, user_id=None):
    """Trigger cedula validation refresh (leader only).

    Rate limited to 30 seconds between refreshes.
    Leaders can refresh their own data or data for users they referred.
    """
    # Determine target user
    if user_id is None:
        target_user = request.user
    else:
        target_user = CustomUser.objects.filter(id=user_id).first()
        if not target_user:
            return HttpResponseForbidden("Usuario no encontrado.")

    cedula_info = getattr(target_user, 'cedula_info', None)

    # Rate limiting: 30 second cooldown
    if cedula_info and cedula_info.fetched_at:
        cooldown_until = cedula_info.fetched_at + timedelta(seconds=30)
        if timezone.now() < cooldown_until:
            # Return current section with error message via HX-Trigger
            response = render(request, 'partials/_census_section.html', {
                'cedula_info': cedula_info,
                'is_polling': False,
                'user': target_user,
                'is_leader': request.user.role == CustomUser.Role.LEADER,
                'show_refresh': True,
            })
            response['HX-Trigger'] = '{"showToast": {"message": "Espera 30 segundos antes de actualizar de nuevo", "type": "warning"}}'
            return response

    # Set status to PROCESSING immediately (avoid race condition)
    if cedula_info:
        cedula_info.status = CedulaInfo.Status.PROCESSING
        cedula_info.fetched_at = timezone.now()  # Reset for cooldown
        cedula_info.save(update_fields=['status', 'fetched_at'])

    # Queue async task
    async_task('accounts.tasks.validate_cedula', target_user.id, 1)

    # Return updated section
    response = render(request, 'partials/_census_section.html', {
        'cedula_info': cedula_info,
        'is_polling': True,
        'user': target_user,
        'is_leader': request.user.role == CustomUser.Role.LEADER,
        'show_refresh': True,
    })
    response['HX-Trigger'] = '{"showToast": {"message": "Actualizacion en progreso", "type": "info"}}'
    return response


class CustomLoginView(LoginView):
    """Login view with remember me functionality"""
    template_name = 'registration/login.html'

    def form_valid(self, form):
        """Handle remember me checkbox"""
        response = super().form_valid(form)
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            # Expire session on browser close
            self.request.session.set_expiry(0)
        else:
            # Set session to 14 days (1209600 seconds)
            self.request.session.set_expiry(1209600)
        return response


class CustomPasswordChangeView(PasswordChangeView):
    """Password change view with custom template and success handling"""
    template_name = 'registration/password_change.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('perfil')

    def form_valid(self, form):
        """Add success message after password change"""
        messages.success(self.request, 'Contrasena actualizada correctamente')
        return super().form_valid(form)


@login_required
def bulk_refresh_view(request):
    """Bulk refresh census data for selected referrals (leader only)."""
    # RBAC check
    if request.user.role != CustomUser.Role.LEADER:
        return HttpResponseForbidden("No tienes permiso para esta accion.")

    # Get selected IDs from POST
    ids = request.POST.getlist('ids')
    if not ids:
        response = render(request, 'partials/_empty_response.html', {})
        response['HX-Trigger'] = '{"showToast": {"message": "No se seleccionaron usuarios", "type": "warning"}}'
        return response

    # Limit to max 10
    ids = ids[:10]

    # Query referrals (only those referred by this leader)
    referrals = CustomUser.objects.filter(id__in=ids, referred_by=request.user)

    refreshed = 0
    for referral in referrals:
        cedula_info = getattr(referral, 'cedula_info', None)
        if not cedula_info:
            continue

        # Skip final statuses
        if cedula_info.status in ['ACTIVE', 'CANCELLED_DECEASED', 'CANCELLED_OTHER', 'PROCESSING']:
            continue

        # Cooldown check (30 seconds)
        if cedula_info.fetched_at:
            cooldown_until = cedula_info.fetched_at + timedelta(seconds=30)
            if timezone.now() < cooldown_until:
                continue

        # Set to PROCESSING and update timestamp
        cedula_info.status = CedulaInfo.Status.PROCESSING
        cedula_info.fetched_at = timezone.now()
        cedula_info.save(update_fields=['status', 'fetched_at'])

        # Queue async task
        async_task('accounts.tasks.validate_cedula', referral.id, 1)
        refreshed += 1

    # Return response with toast
    response = render(request, 'partials/_empty_response.html', {})
    if refreshed > 0:
        response['HX-Trigger'] = f'{{"showToast": {{"message": "{refreshed} cedulas en actualizacion", "type": "info"}}}}'
    else:
        response['HX-Trigger'] = '{"showToast": {"message": "Todas las cedulas seleccionadas fueron actualizadas recientemente", "type": "warning"}}'

    return response


@login_required
def referral_row_view(request, referral_id):
    """Return single referral row partial for HTMX updates."""
    # RBAC check
    if request.user.role != CustomUser.Role.LEADER:
        return HttpResponseForbidden("No tienes permiso para esta accion.")

    # Get referral (only if referred by this user)
    from django.shortcuts import get_object_or_404
    referral = get_object_or_404(CustomUser, id=referral_id, referred_by=request.user)

    return render(request, 'partials/_referral_row.html', {
        'referral': referral,
        'is_leader': True,
    })


@login_required
def referidos_view(request):
    """View showing users referred by the current user."""
    referrals = request.user.referrals.prefetch_related('cedula_info').all().order_by('-date_joined')
    is_leader = request.user.role == CustomUser.Role.LEADER
    referral_url = request.build_absolute_uri(reverse('register') + f'?ref={request.user.referral_code}')

    return render(request, 'referidos.html', {
        'referrals': referrals,
        'is_leader': is_leader,
        'referral_url': referral_url,
    })
