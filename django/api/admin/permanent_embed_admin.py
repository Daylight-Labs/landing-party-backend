from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.admin.widgets import AutocompleteSelectMultiple

from api.models import GuidedFlow, GuidedFlowStep, PermanentEmbed, PermanentEmbedButton, AbstractBotEventHandler,\
    PermanentEmbedAttachedFile

class FixedWidthAutocompleteForm(forms.ModelForm):
    class Meta:
        exclude = ('deleted_on', )
        widgets = {
            'triggered_handlers': AutocompleteSelectMultiple(
                GuidedFlow._meta.get_field('triggered_handlers'),
                admin.site,
                attrs={'style': 'width: 620px'}
            ),
            'handler_callbacks': AutocompleteSelectMultiple(
                GuidedFlow._meta.get_field('handler_callbacks'),
                admin.site,
                attrs={'style': 'width: 620px'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(FixedWidthAutocompleteForm, self).__init__(*args, **kwargs)  # populates the post
        self.fields['triggered_handlers'].queryset = \
            AbstractBotEventHandler.objects.filter(guidedflow__id__isnull=False)

class PermanentEmbedButtonInline(admin.TabularInline):
    model = PermanentEmbedButton
    fk_name = "embed"
    form = FixedWidthAutocompleteForm

class PermanentEmbedFileInline(admin.TabularInline):
    model = PermanentEmbedAttachedFile
    fields = ['name', 'file']

class PermanentEmbedAdmin(admin.ModelAdmin):
    class Meta:
        model = PermanentEmbed

    exclude = ('deleted_on', 'channel_entrypoint_id')

    autocomplete_fields = ("community", "channel_entrypoint_ref")

    inlines = [PermanentEmbedButtonInline, PermanentEmbedFileInline]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        field = super(PermanentEmbedAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == 'channel_entrypoint_ref':
            url = request.get_full_path()
            permanent_embed_id = url.split('/')[-3]
            if permanent_embed_id.isnumeric():
                permanent_embed = PermanentEmbed.objects.filter(pk=permanent_embed_id).first()
                if permanent_embed is not None:
                    community = permanent_embed.community
                    field.queryset = field.queryset.filter(channel_community=community).order_by('channel_name')

        return field

admin.site.register(PermanentEmbed, PermanentEmbedAdmin)