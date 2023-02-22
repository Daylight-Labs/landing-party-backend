from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms

from api.models import Community, User, EventLog
from django.contrib.admin.filters import (
    AllValuesFieldListFilter,
)

def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = AllValuesFieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper

class EventLogAdmin(admin.ModelAdmin):
    class Meta:
        model = EventLog

    list_display = ['id', 'community' , 'type', 'user_prompt', 'bot_response', 'created_on', 'is_spam']

    list_filter = ['type', ('community__slug', custom_titled_filter('Community') ), 'is_spam']

    search_fields = ('user_prompt', 'bot_response', 'slackbot_log')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        # to test kicking after sending spam
        return True

    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(EventLog, EventLogAdmin)