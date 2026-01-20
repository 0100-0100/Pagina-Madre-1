from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django_q import models as q_models
from django_q import admin as q_admin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # Display custom fields in admin list view
    list_display = UserAdmin.list_display + (
        'cedula', 'phone', 'referral_code', 'referred_by', 'referral_goal'
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
    )

    # Include custom fields when adding new user via admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('cedula', 'nombre_completo', 'phone', 'data_policy_accepted')
        }),
    )


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
