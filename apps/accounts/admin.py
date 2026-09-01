from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'organization', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'organization')
    fieldsets = UserAdmin.fieldsets + (
        ('SafariFlow Multi-Tenancy', {'fields': ('organization', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('SafariFlow Multi-Tenancy', {'fields': ('organization', 'role')}),
    )

admin.site.register(User, CustomUserAdmin)
