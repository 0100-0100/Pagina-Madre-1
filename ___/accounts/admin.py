from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django_q import models as q_models
from django_q import admin as q_admin
from .models import CustomUser, CedulaInfo


@admin.register(CedulaInfo)
class CedulaInfoAdmin(admin.ModelAdmin):
    """Read-only admin for CedulaInfo - data comes from scraping only."""

    list_display = (
        'user',
        'status',
        'departamento',
        'municipio',
        'puesto',
        'direccion',
        'mesa',
        'novedad',
        'resolucion',
        'fecha_novedad',
        'fetched_at',
        'error_message',
    )
    list_filter = ('status', 'departamento')
    search_fields = (
        'user__cedula',
        'user__nombre_completo',
        'municipio',
        'puesto',
    )
    ordering = ('-fetched_at',)

    def get_readonly_fields(self, request, obj=None):
        """Make all fields read-only."""
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CustomUserAdmin(UserAdmin):
    # Display custom fields in admin list view
    list_display = UserAdmin.list_display + (
        'cedula', 'phone', 'referral_code', 'referred_by', 'referral_goal', 'role'
    )

    # Make referral_code read-only (auto-generated)
    readonly_fields = ('referral_code',)

    # Add custom fields to admin detail view
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('cedula', 'nombre_completo', 'phone', 'data_policy_accepted')
        }),
        ('Referral Info', {
            'fields': ('referral_code', 'referred_by', 'referral_goal')
        }),
        ('Role', {
            'fields': ('role',),
            'description': 'Solo superadmins pueden cambiar roles',
        }),
    )

    # Include custom fields when adding new user via admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('cedula', 'nombre_completo', 'phone', 'data_policy_accepted')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """Make role read-only for non-superusers."""
        readonly = list(self.readonly_fields)
        if not request.user.is_superuser:
            readonly.append('role')
        return readonly


admin.site.register(CustomUser, CustomUserAdmin)


# Django-Q2 Admin Customization
# Unregister default Failure admin and register enhanced version
admin.site.unregister([q_models.Failure])


@admin.register(q_models.Failure)
class FailureAdmin(q_admin.FailAdmin):
    """Enhanced failed task admin with attempt count and error details."""
    list_display = (
        'name',
        'func',
        'started',
        'stopped',
        'time_taken',
        'attempt_count',
        'short_result',
    )
    list_filter = ('group', 'cluster', 'started')
