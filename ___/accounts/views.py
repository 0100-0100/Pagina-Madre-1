from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse
from .forms import CustomUserCreationForm


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Try to redirect to 'home', fallback to admin if not available
            try:
                return redirect('home')
            except:
                return redirect('/admin/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


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
