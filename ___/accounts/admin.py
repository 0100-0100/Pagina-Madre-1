from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # Display custom fields in admin list view
    list_display = UserAdmin.list_display + ('cedula', 'phone', 'data_policy_accepted')

    # Add custom fields to admin detail view
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('cedula', 'nombre_completo', 'phone', 'data_policy_accepted')}),
    )

    # Include custom fields when adding new user via admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('cedula', 'nombre_completo', 'phone', 'data_policy_accepted')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
