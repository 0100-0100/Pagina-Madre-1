from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from .forms import CustomUserCreationForm, ProfileForm, CustomPasswordChangeForm


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


def placeholder_view(request):
    """Placeholder view for routes not yet implemented."""
    return HttpResponse("Coming soon", status=200)


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

    return render(request, 'profile.html', {
        'form': form,
        'user': request.user,
    })


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
