from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse
from .forms import CustomUserCreationForm


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
    """Home page view"""
    return render(request, 'home.html', {'user': request.user})


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
