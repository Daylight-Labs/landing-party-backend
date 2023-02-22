from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms

from api.models.user import User
from api.models.user_roleset import UserRoleSet

class RoleSetInline(admin.TabularInline):
    model = UserRoleSet

    verbose_name = "Synced Discord Role (readonly)"
    verbose_name_plural = "Synced Discord Roles (readonly)"

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

class UserAdmin(admin.ModelAdmin):
    class Meta:
        model = User

    search_fields = ("discord_user_id", "discord_username", "email")

    list_display = [
        'id', 
        'discord_username',
        'discord_user_id',
        'date_registered',
        'email',
        'is_active',
        'is_superuser',
        'is_staff'
    ]

    inlines = [RoleSetInline]

    fields = ['discord_user_id', 'discord_username', 'email']

admin.site.register(User, UserAdmin)