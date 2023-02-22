from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms

from api.models import Community, User, DiscordChannel

class DiscordChannelAdmin(admin.ModelAdmin):
    class Meta:
        model = DiscordChannel

    def has_add_permission(self, request):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return True

    def has_change_permission(self, request, obj=None):
        return False

    search_fields = ('channel_id', 'channel_name')

admin.site.register(DiscordChannel, DiscordChannelAdmin)