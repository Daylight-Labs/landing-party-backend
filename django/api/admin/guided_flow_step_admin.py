from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from api.models import GuidedFlow, GuidedFlowStep, GuidedFlowStepButton, GuidedFlowStepAttachedFile, \
    InviteUsersToCurrentThread, AbstractBotEvent, AbstractBotEventHandler, InviteUsersWithRoleToCurrentThread, \
    ShowTicketModal, ShowCustomModal, CustomModalField, ShowSelectMenu, SelectMenuOption, ShowCaptcha, \
    EventRecord, GrantRole
from .event_log_admin import custom_titled_filter
from django.contrib.admin import SimpleListFilter
from django.utils.safestring import mark_safe
import io
from django.http import HttpResponse
import csv

@admin.action(description='Duplicate step(s)')
def duplicate_step(modeladmin, request, queryset):
    for step in queryset:
        cpy = step.copy(None)
        for b in step.step_buttons.all():
            b.copy(flow_step=cpy)

class FixedWidthAutocompleteForm(forms.ModelForm):
    class Meta:
        fields = ['button_label', 'button_style', 'button_row', 'triggered_handlers', 'handler_callbacks']
        widgets = {
            'triggered_handlers': AutocompleteSelectMultiple(
                GuidedFlowStepButton._meta.get_field('triggered_handlers'),
                admin.site,
                attrs={'style': 'width: 620px'}
            ),
            'handler_callbacks': AutocompleteSelectMultiple(
                GuidedFlowStepButton._meta.get_field('handler_callbacks'),
                admin.site,
                attrs={'style': 'width: 620px'}
            ),
        }


class FlowStepFixedWidthAutocompleteForm(forms.ModelForm):
    class Meta:
        fields = ['guided_flow', 'step_text', 'help_text', 'granted_role_id',
                  'granted_role_needs_approval_by',
                  'file_upload_triggered_handlers',
                  'supported_files_formats_csv']
        widgets = {
            'file_upload_triggered_handlers': AutocompleteSelectMultiple(
                GuidedFlowStep._meta.get_field('file_upload_triggered_handlers'),
                admin.site,
                attrs={'style': 'width: 620px'}
            ),
        }

class AbstractBotEventAdmin(admin.ModelAdmin):
    class Meta:
        model = AbstractBotEvent
    # search_fields = ("id",)
    def get_model_perms(self, request):
        # Hide Abstract Bot Event Admin
        return {}

class EventHandleFlowFilter(SimpleListFilter):
    title = 'Flow'
    parameter_name = 'flow'

    def lookups(self, request, model_admin):
        return [(f.id, f.flow_label) for f in GuidedFlow.objects.all()]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        flow = GuidedFlow.objects.get(id=self.value())
        output_json = []
        flow.create_copy_recursive(flow, None, serialize_to_array_not_db=output_json,
                                   crash_in_case_of_subflow=False)

        event_handler_ids = []

        for item in output_json:
            if 'event_handler_id' in item:
                event_handler_ids.append(item['event_handler_id'])

        return queryset.filter(event_handler_id__in=event_handler_ids)

class AbstractBotEventHandlerAdmin(admin.ModelAdmin):
    class Meta:
        model = AbstractBotEventHandler

    def has_add_permission(self, request):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return False

    def has_change_permission(self, request, obj=None):
        return False

    search_fields = ("id",)

    list_filter = (EventHandleFlowFilter,)

    list_display = ('linkable_str',)

    def linkable_str(self, obj):
        event_handler = obj.as_leaf_class()
        if type(event_handler) == GuidedFlow:
            return mark_safe(u'<a href="/admin/api/guidedflow/%s/change">%s</a>' % (event_handler.id, str(obj)))
        if type(event_handler) == GuidedFlowStep:
            return mark_safe(u'<a href="/admin/api/guidedflowstep/%s/change">%s</a>' % (event_handler.id, str(obj)))
        if type(event_handler) == ShowSelectMenu:
            return mark_safe(u'<a href="/admin/api/showselectmenu/%s/change">%s</a>' % (event_handler.id, str(obj)))
        if type(event_handler) == ShowCustomModal:
            return mark_safe(u'<a href="/admin/api/showcustommodal/%s/change">%s</a>' % (event_handler.id, str(obj)))
        if type(event_handler) == InviteUsersToCurrentThread:
            return mark_safe(
                u'<a href="/admin/api/inviteuserstocurrentthread/%s/change">%s</a>' % (event_handler.event_handler_id,
                                                                                       str(obj)))
        if type(event_handler) == ShowTicketModal:
            return mark_safe(u'<a href="/admin/api/showticketmodal/%s/change">%s</a>' % (event_handler.event_handler_id,
                                                                                         str(obj)))
        if type(event_handler) == GrantRole:
            return mark_safe(u'<a href="/admin/api/grantrole/%s/change">%s</a>' % (event_handler.event_handler_id,
                                                                                   str(obj)))
        return str(obj)

    linkable_str.allow_tags = True
    linkable_str.short_description = ""

    def __init__(self, *args, **kwargs):
        super(AbstractBotEventHandlerAdmin, self).__init__(*args, **kwargs)

    # Custom autocomplete search logic
    def get_search_results(self, request, queryset, search_term):
        search_tokens = list(map(lambda x: x.lower(), search_term.split()))
        filtered_items = []
        for item in queryset:
            str_rep = str(item).lower()
            matches = True
            for tok in search_tokens:
                if tok not in str_rep:
                    matches = False
                    break
            if matches:
                filtered_items.append((item.pk, str_rep))
        filtered_items.sort(key=lambda x: x[1])
        filtered_ids = list(map(lambda x: x[0], filtered_items))
        clauses = ' '.join(['WHEN event_handler_id=%s THEN %s' % (pk, i) for i, pk in enumerate(filtered_ids)])
        ordering = 'CASE %s END' % clauses
        return queryset.filter(pk__in=filtered_ids).extra(
           select={'ordering': ordering}, order_by=('ordering',)), False

# Needed in order to use autocomplete fields
admin.site.register(AbstractBotEventHandler, AbstractBotEventHandlerAdmin)
admin.site.register(AbstractBotEvent, AbstractBotEventAdmin)

class GuidedFlowStepButtonInline(admin.TabularInline):
    model = GuidedFlowStepButton
    fk_name = "flow_step"
    form = FixedWidthAutocompleteForm

class GuidedFlowStepFileInline(admin.TabularInline):
    model = GuidedFlowStepAttachedFile
    fields = ['name', 'file']

class GuidedFlowStepAdmin(admin.ModelAdmin):
    class Meta:
        model = GuidedFlowStep

    autocomplete_fields = ("granted_role_needs_approval_by",)

    form = FlowStepFixedWidthAutocompleteForm

    actions = [duplicate_step]

    exclude = ('deleted_on', 'attached_files')

    inlines = [GuidedFlowStepButtonInline, GuidedFlowStepFileInline]

    list_per_page = 500

    list_filter = [('guided_flow__community__slug', custom_titled_filter('Community')),
                   ('guided_flow__flow_label', custom_titled_filter('Flow'))]

admin.site.register(GuidedFlowStep, GuidedFlowStepAdmin)

class InviteUsersToCurrentThreadAdmin(admin.ModelAdmin):
    class Meta:
        model = InviteUsersToCurrentThread

    exclude = ('deleted_on',)
    autocomplete_fields = ("users_to_invite",)

admin.site.register(InviteUsersToCurrentThread, InviteUsersToCurrentThreadAdmin)

class GrantRoleAdmin(admin.ModelAdmin):
    class Meta:
        model = GrantRole

    autocomplete_fields = ("granted_role_needs_approval_by",)
    exclude = ('deleted_on',)

admin.site.register(GrantRole, GrantRoleAdmin)

class InviteUsersWithRoleToCurrentThreadAdmin(admin.ModelAdmin):
    class Meta:
        model = InviteUsersWithRoleToCurrentThread

    exclude = ('deleted_on',)

admin.site.register(InviteUsersWithRoleToCurrentThread, InviteUsersWithRoleToCurrentThreadAdmin)

@admin.action(description='Duplicate ticket modal(s)')
def duplicate_ticket_modal(modeladmin, request, queryset):
    for modal in queryset:
        modal.copy(None)

class TicketModalFixedWidthAutocompleteForm(forms.ModelForm):
    class Meta:
        fields = ['triggered_handlers', 'handler_callbacks', 'label',
                  'modal_title', 'subject_label', 'subject_placeholder',
                  'describe_label', 'describe_placeholder']
        widgets = {
            'triggered_handlers': AutocompleteSelectMultiple(
                GuidedFlowStepButton._meta.get_field('triggered_handlers'),
                admin.site,
                attrs={'style': 'width: 620px'}
            ),
            'handler_callbacks': AutocompleteSelectMultiple(
                GuidedFlowStepButton._meta.get_field('handler_callbacks'),
                admin.site,
                attrs={'style': 'width: 620px'}
            ),
        }

class ShowTicketModalAdmin(admin.ModelAdmin):
    class Meta:
        model = ShowTicketModal

    form = TicketModalFixedWidthAutocompleteForm
    actions = [duplicate_ticket_modal]

admin.site.register(ShowTicketModal, ShowTicketModalAdmin)

@admin.action(description='Duplicate captcha(s)')
def duplicate_captcha(modeladmin, request, queryset):
    for captcha in queryset:
        captcha.copy(None)

class ShowCaptchaFixedWidthAutocompleteForm(forms.ModelForm):
    class Meta:
        fields = ['triggered_handlers', 'captcha_type', 'handler_callbacks', 'captcha_message', 'verify_button_text', 'label']
        widgets = {
            'triggered_handlers': AutocompleteSelectMultiple(
                GuidedFlowStepButton._meta.get_field('triggered_handlers'),
                admin.site,
                attrs={'style': 'width: 620px'}
            ),
            'handler_callbacks': AutocompleteSelectMultiple(
                GuidedFlowStepButton._meta.get_field('handler_callbacks'),
                admin.site,
                attrs={'style': 'width: 620px'}
            ),
        }

class ShowCaptchaAdmin(admin.ModelAdmin):
    class Meta:
        model = ShowCaptcha
    
    form = ShowCaptchaFixedWidthAutocompleteForm
    actions = [duplicate_captcha]

admin.site.register(ShowCaptcha, ShowCaptchaAdmin)

class ModalFieldInline(admin.TabularInline):
    model = CustomModalField
    # fk_name = "flow_step"
    exclude = ('deleted_on',)

class CustomModalFixedWidthAutocompleteForm(forms.ModelForm):
    class Meta:
        fields = ['title', 'triggered_handlers', 'handler_callbacks', 'label', 'csv_export_is_anonymous',
                  'google_spreadsheet_id', 'anonymized_google_spreadsheet_id']
        widgets = {
            'triggered_handlers': AutocompleteSelectMultiple(
                GuidedFlowStepButton._meta.get_field('triggered_handlers'),
                admin.site,
                attrs={'style': 'width: 620px'}
            ),
            'handler_callbacks': AutocompleteSelectMultiple(
                GuidedFlowStepButton._meta.get_field('handler_callbacks'),
                admin.site,
                attrs={'style': 'width: 620px'}
            ),
        }

def encode_discord_user_id(user_id):
    crypto_key = int('10101010101010101010101010101010101010101010101010101010101', base=2)
    return user_id ^ crypto_key

def export_modal_submissions_to_csv(queryset, force_anonymized=None):
    event_ptrs = []
    anonymized_event_ptrs = []

    for modal in queryset:
        if force_anonymized or (modal.csv_export_is_anonymous and force_anonymized is None):
            anonymized_event_ptrs.append(modal.abstractbotevent_ptr)
        else:
            event_ptrs.append(modal.abstractbotevent_ptr)

    records = EventRecord.objects.filter(event__in=event_ptrs)
    anonymized_records = EventRecord.objects.filter(event__in=anonymized_event_ptrs)

    field_names = []
    for record in records:
        field_names.extend(list(record.record.keys()))
    for record in anonymized_records:
        field_names.extend(list(record.record.keys()))
    field_names = list(set(field_names))

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow([
                        'Record Id',
                        'Time Posted',
                        'Channel Id',
                        'Guild Id',
                        'Discord User Id',
                        'Discord Username'
                    ] + field_names)
    for record in records:
        field_values = []
        for f_name in field_names:
            field_values.append(record.record.get(f_name, ''))
        writer.writerow([
                            record.pk,
                            record.created_on,
                            record.channel_id,
                            record.guild_id,
                            record.discord_user_id,
                            record.discord_user_name
                        ] + field_values)
    for record in anonymized_records:
        field_values = []
        for f_name in field_names:
            field_values.append(record.record.get(f_name, ''))
        writer.writerow([
                            record.pk,
                            record.created_on,
                            record.channel_id,
                            record.guild_id,
                            str(encode_discord_user_id(record.discord_user_id)) + ' (ANONYMIZED)',
                            'ANONYMOUS'
                        ] + field_values)

    return output

@admin.action(description='Export submissions as CSV')
def export_modal_csv(modeladmin, request, queryset):
    output = export_modal_submissions_to_csv(queryset)
    response = HttpResponse(output.getvalue())
    response['Content-Disposition'] = 'attachment; filename="modal_submissions.csv"'
    return response

@admin.action(description='Duplicate modal(s)')
def duplicate_modal(modeladmin, request, queryset):
    for modal in queryset:
        modal.copy(None)

class ShowCustomModalAdmin(admin.ModelAdmin):
    class Meta:
        model = ShowCustomModal

    inlines = [ModalFieldInline]
    form = CustomModalFixedWidthAutocompleteForm
    actions = [export_modal_csv, duplicate_modal]

    exclude = ('deleted_on', )

admin.site.register(ShowCustomModal, ShowCustomModalAdmin)

class SelectOptionFixedWidthAutocompleteForm(forms.ModelForm):
    class Meta:
        fields = ['label', 'description', 'order', 'triggered_handlers', 'handler_callbacks']
        widgets = {
            'triggered_handlers': AutocompleteSelectMultiple(
                GuidedFlowStepButton._meta.get_field('triggered_handlers'),
                admin.site,
                attrs={'style': 'width: 620px'}
            ),
            'handler_callbacks': AutocompleteSelectMultiple(
                GuidedFlowStepButton._meta.get_field('handler_callbacks'),
                admin.site,
                attrs={'style': 'width: 620px'}
            ),
        }

class SelectOptionInline(admin.TabularInline):
    model = SelectMenuOption
    fk_name = "menu"
    exclude = ('deleted_on',)
    ordering = ("order",)
    form = SelectOptionFixedWidthAutocompleteForm

class SelectMenuFixedWidthAutocompleteForm(forms.ModelForm):
    class Meta:
        fields = ['message_text', 'placeholder', 'min_values', 'max_values', 'triggered_handlers', 'handler_callbacks',
                  'label', 'csv_export_is_anonymous', 'google_spreadsheet_id', 'anonymized_google_spreadsheet_id']
        widgets = {
            'triggered_handlers': AutocompleteSelectMultiple(
                GuidedFlowStepButton._meta.get_field('triggered_handlers'),
                admin.site,
                attrs={'style': 'width: 620px'}
            ),
            'handler_callbacks': AutocompleteSelectMultiple(
                GuidedFlowStepButton._meta.get_field('handler_callbacks'),
                admin.site,
                attrs={'style': 'width: 620px'}
            ),
        }

def export_menu_submissions_to_csv(queryset, force_anonymized=None):
    event_ptrs = []
    anonymized_event_ptrs = []

    for menu in queryset:
        if force_anonymized or (menu.csv_export_is_anonymous and force_anonymized is None):
            anonymized_event_ptrs.append(menu.abstractbotevent_ptr)
        else:
            event_ptrs.append(menu.abstractbotevent_ptr)

    records = EventRecord.objects.filter(event__in=event_ptrs)
    anonymized_records = EventRecord.objects.filter(event__in=anonymized_event_ptrs)

    field_names = []
    for record in records:
        field_names.extend(record.record)
    for record in anonymized_records:
        field_names.extend(record.record)
    field_names = list(set(field_names))

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow([
                        'Record Id',
                        'Time Posted',
                        'Channel Id',
                        'Guild Id',
                        'Discord User Id',
                        'Discord Username'
                    ] + field_names)
    for record in records:
        field_values = []
        for f_name in field_names:
            field_values.append('1' if f_name in record.record else '0')
        writer.writerow([
                            record.pk,
                            record.created_on,
                            record.channel_id,
                            record.guild_id,
                            record.discord_user_id,
                            record.discord_user_name
                        ] + field_values)
    for record in anonymized_records:
        field_values = []
        for f_name in field_names:
            field_values.append('1' if f_name in record.record else '0')
        writer.writerow([
                            record.pk,
                            record.created_on,
                            record.channel_id,
                            record.guild_id,
                            str(encode_discord_user_id(record.discord_user_id)) + ' (ANONYMIZED)',
                            'ANONYMOUS'
                        ] + field_values)
    return output

@admin.action(description='Export submissions as CSV')
def export_menu_csv(modeladmin, request, queryset):
    output = export_menu_submissions_to_csv(queryset)
    response = HttpResponse(output.getvalue())
    response['Content-Disposition'] = 'attachment; filename="modal_submissions.csv"'
    return response

@admin.action(description='Duplicate menu(s)')
def duplicate_menu(modeladmin, request, queryset):
    for menu in queryset:
        copy = menu.copy(None)
        for o in menu.options.all():
            o_copy = o.copy(menu=copy)
            copy.options.add(o_copy)

class ShowSelectMenuAdmin(admin.ModelAdmin):
    class Meta:
        model = ShowSelectMenu

    inlines = [SelectOptionInline]
    actions = [export_menu_csv, duplicate_menu]

    form = SelectMenuFixedWidthAutocompleteForm

admin.site.register(ShowSelectMenu, ShowSelectMenuAdmin)