from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.db import transaction
from django.http import HttpResponse
import io
import csv

from api.models import Community, User, BotEnabledDiscordChannel, EventLog, DiscordChannel, QaDocument

class AdminsInline(admin.TabularInline):
    model = Community.admins.through
    # Comment below line out if CSS does not work (locally)
    autocomplete_fields = ("user",)

class BotEnabledDiscordChannelInline(admin.TabularInline):
    model = BotEnabledDiscordChannel
    fields = ['channel_ref']

    autocomplete_fields = ("channel_ref",)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        field = super(BotEnabledDiscordChannelInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == 'channel_ref':
            if request._obj_ is not None:
                field.queryset = field.queryset.filter(channel_community=request._obj_).order_by('channel_name')
            else:
                field.queryset = field.queryset.none()

        return field

@admin.action(description='Export FAQ stats as CSV')
def export_faq_stats_csv(modeladmin, request, queryset):
    from api.utils.spreadsheet_util import export_faq_bot_stats_to_csv
    community = queryset.first()
    output = export_faq_bot_stats_to_csv(community.guild_id)
    response = HttpResponse(output.getvalue())
    response['Content-Disposition'] = 'attachment; filename="faq_stats.csv"'
    return response

@admin.action(description='Export QA Documents')
def export_qadocuments(modeladmin, request, queryset):
    community = queryset.first()

    qa_documents = QaDocument.objects.filter(guild_id=community.guild_id)
    
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow([
        'Prompt',
        'Completion'
    ])
    for document in qa_documents:
        writer.writerow([
            document.prompt,
            document.completion
        ])
    response = HttpResponse(output.getvalue())
    response['Content-Disposition'] = 'attachment; filename="qa_documents.csv"'
    return response

class CommunityForm(forms.ModelForm):

    add_all_community_channels = forms.BooleanField(required=False)

    def save(self, commit=True):
        add_all_community_channels = self.cleaned_data.pop('add_all_community_channels', None)
        community = super(CommunityForm, self).save(commit=commit)
        if add_all_community_channels:
            for ch in DiscordChannel.objects.filter(channel_community=community):
                BotEnabledDiscordChannel.objects.create(
                    channel_ref=ch,
                    community=community
                )
            self.add_error('add_all_community_channels', 'Done. Now refresh the page to see all channels added')
        return community

    class Meta:
        model = Community
        fields = ['name', 'slug', 'guild_id', 'is_active', 'minimum_threshold', 'add_all_community_channels',
                  'admin_role_ids', 'verified_role_id', 'kick_users_who_joined_but_did_not_verify_after_days',
                  'kick_users_who_joined_but_did_not_verify_after_hours',
                  'kick_users_ignore_datetime_before_utc', 'kick_users_who_sent_spam_times',
                  'faq_bot_google_spreadsheet_id']

class CommunityAdmin(admin.ModelAdmin):
    class Meta:
        model = Community

    list_display = ['id', 'name', 'slug', 'guild_id', 'is_active', 'minimum_threshold']

    search_fields = ("id", "name", "slug", "guild_id")

    inlines = [AdminsInline, BotEnabledDiscordChannelInline]
    actions = [export_faq_stats_csv, export_qadocuments]

    form = CommunityForm

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super(CommunityAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        previous_guild_id = None
        new_guild_id = obj.guild_id
        if obj.pk:
            previous_guild_id = Community.objects.get(pk=obj.pk).guild_id
        if obj.pk and str(previous_guild_id) != str(new_guild_id):
            with transaction.atomic():
                EventLog.objects.filter(community_id=previous_guild_id).update(community_id=new_guild_id)
                super().save_model(request, obj, form, change)
        else:
            super().save_model(request, obj, form, change)

admin.site.register(Community, CommunityAdmin)