# custom_auth/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

class CustomUserAdmin(UserAdmin):
    model = User
    # Remove is_staff from list display
    list_display = ('username', 'email', 'first_name', 'last_name', 'display_profile_image')
    list_filter = ('is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'profile_image')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'profile_image'),
        }),
    )
    
    def display_profile_image(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="50" height="50" />', obj.profile_image.url)
        return "-"
    display_profile_image.short_description = 'Profile Image'

    # Remove is_staff from form fields
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'is_staff' in form.base_fields:
            del form.base_fields['is_staff']
        return form

admin.site.register(User, CustomUserAdmin)
