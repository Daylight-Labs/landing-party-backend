from django.contrib import admin
from django import forms

from api.models.event_record import EventRecord
from api.admin.event_log_admin import custom_titled_filter

class EventRecordAdmin(admin.ModelAdmin):
    class Meta:
        model = EventRecord

    def qa_document_count(self, obj):
        return obj.qa_documents.count()

    list_display = [
        'event',
        'record',
        'source',
        'channel_id',
        'guild_id',
        'discord_user_id',
        'discord_user_name'
    ]

    list_filter = [
         ('event', custom_titled_filter('Bot Event') ),
         ('guild_id', custom_titled_filter('Discord Server') ),
         ('discord_user_id', custom_titled_filter('Discrod User') ),
    ]

    search_fields = ('record', 'channel_id', 'guild_id', 'discord_user_id')

admin.site.register(EventRecord, EventRecordAdmin)