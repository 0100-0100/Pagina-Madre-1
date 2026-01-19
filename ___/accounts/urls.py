from django.urls import path
from .views import register, CustomLoginView, home, placeholder_view, profile_view, CustomPasswordChangeView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', profile_view, name='perfil'),
    path('cambiar-password/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('referidos/', placeholder_view, name='referidos'),
]
