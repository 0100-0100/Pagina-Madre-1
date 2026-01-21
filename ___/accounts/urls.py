from django.urls import path
from .views import register, CustomLoginView, home, profile_view, CustomPasswordChangeView, referidos_view, census_section_view
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', profile_view, name='perfil'),
    path('censo/', census_section_view, name='census_section'),
    path('cambiar-password/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('referidos/', referidos_view, name='referidos'),
]
