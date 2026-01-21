from django.urls import path
from .views import (
    register, CustomLoginView, home, profile_view, CustomPasswordChangeView,
    referidos_view, census_section_view, refresh_cedula_view,
    bulk_refresh_view, referral_row_view
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', profile_view, name='perfil'),
    path('censo/', census_section_view, name='census_section'),
    path('refrescar-cedula/', refresh_cedula_view, name='refresh_cedula'),
    path('refrescar-cedula/<int:user_id>/', refresh_cedula_view, name='refresh_cedula_user'),
    path('cambiar-password/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('referidos/', referidos_view, name='referidos'),
    path('bulk-refresh/', bulk_refresh_view, name='bulk_refresh'),
    path('referido/<int:referral_id>/', referral_row_view, name='referral_row'),
]
