from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.db import transaction
from django.conf import settings
import os
import io
import csv
from django.http import HttpResponse
import requests
from api.models.abstract_bot_event_handler import EVENT_HANDLER_TYPE_SHOW_SELECT_MENU, EVENT_HANDLER_TYPE_SHOW_CUSTOM_MODAL

from api.models import GuidedFlow, GuidedFlowStep, PermanentEmbed, PermanentEmbedButton, \
    InviteUsersWithRoleToCurrentThread, ShowSelectMenu, ShowCustomModal, EventRecord, SelectMenuOption, \
    CustomModalField

from api.admin.guided_flow_step_admin import encode_discord_user_id

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

MIGRATE_TO = "prod" if settings.ENVIRONMENT == "staging" else "staging"
MIGRATE_ENV_URL = "https://api.app.background.network" if MIGRATE_TO == "prod" \
    else "https://api.staging.app.background.network"

@admin.action(description='Duplicate flow (does not work if flow triggers subflows)')
def duplicate_flow(modeladmin, request, queryset):
    with transaction.atomic():
        for flow in queryset:
            flow.create_copy_recursive(flow, None)

@admin.action(description=f'Migrate to {MIGRATE_TO}')
def migrate_flow(modeladmin, request, queryset):
    API_CHATBOT_AUTH_TOKEN = os.environ['CHATBOT_API_AUTH_TOKEN']
    with transaction.atomic():
        for flow in queryset:
            output_json = []
            flow.create_copy_recursive(flow, None, serialize_to_array_not_db=output_json)
            import json
            print(json.dumps(output_json))
            res = requests.post(
                MIGRATE_ENV_URL + '/api/import_guided_flow',
                json={'event_handlers': output_json},
                headers={'auth': API_CHATBOT_AUTH_TOKEN,
                         'Content-Type': 'application/json'}
            )
            print(res.content)
            if res.status_code != 200:
                raise Exception(res.content)


def export_flow_submissions(queryset, only_latest, force_anonymized=None):
    for flow in queryset:
        output_json = []
        flow.create_copy_recursive(flow, None, serialize_to_array_not_db=output_json)

        select_menu_event_ids = list(
            map(lambda x: x['event_id'],
                filter(
                    lambda x: x['handler_type'] == EVENT_HANDLER_TYPE_SHOW_SELECT_MENU,
                    output_json
                )
            ))
        select_menu_queryset = ShowSelectMenu.objects.filter(event_id__in=select_menu_event_ids)
        valid_select_menu_option_names = set()
        for opt in SelectMenuOption.objects.filter(
                menu__in=select_menu_queryset,
                deleted_on__isnull=True
            ):
            valid_select_menu_option_names.add(opt.label)

        custom_modal_event_ids = list(
            map(lambda x: x['event_id'],
                filter(
                    lambda x: x['handler_type'] == EVENT_HANDLER_TYPE_SHOW_CUSTOM_MODAL,
                    output_json
                )
            ))
        custom_modal_queryset = ShowCustomModal.objects.filter(event_id__in=custom_modal_event_ids)
        valid_custom_modal_fields_names = set()
        for fld in CustomModalField.objects.filter(
                modal__in=custom_modal_queryset,
                deleted_on__isnull=True
            ):
            valid_custom_modal_fields_names.add(fld.label)

        event_ptrs = []
        anonymized_event_ptrs = []

        for menu in select_menu_queryset:
            if force_anonymized or (menu.csv_export_is_anonymous and force_anonymized is None):
                anonymized_event_ptrs.append(menu.abstractbotevent_ptr)
            else:
                event_ptrs.append(menu.abstractbotevent_ptr)

        for modal in custom_modal_queryset:
            if force_anonymized or (modal.csv_export_is_anonymous and force_anonymized is None):
                anonymized_event_ptrs.append(modal.abstractbotevent_ptr)
            else:
                event_ptrs.append(modal.abstractbotevent_ptr)

        records = EventRecord.objects.filter(event__in=event_ptrs)
        anonymized_records = EventRecord.objects.filter(event__in=anonymized_event_ptrs)

        SOURCE_MODAL = 'modal'
        SOURCE_SELECT_MENU = 'select-menu'

        def index_records_by_user_and_event_id(records_dict):

            res = {}
            for record in records_dict:
                user_id = record.discord_user_id
                event_id = record.event.event_id
                is_modal = record.source == SOURCE_MODAL
                is_menu = record.source == SOURCE_SELECT_MENU

                if user_id not in res:
                    res[user_id] = {}

                if event_id not in res[user_id]:
                    res[user_id][event_id] = []

                res[user_id][event_id].append(record)

            for u_id in res:
                for e_id in res[u_id]:
                    res[u_id][e_id] = sorted(res[u_id][e_id], key=lambda x: x.created_on)

            return res

        indexed_records = index_records_by_user_and_event_id(records)
        indexed_anonymous_records = index_records_by_user_and_event_id(anonymized_records)

        field_names = []
        event_ids_sequence = []
        record_fields_sequence_by_event_id = {}

        all_records = list(records)
        all_records.extend(list(anonymized_records))

        record_fields_by_event_id = {}
        event_by_event_id = {}

        for record in all_records:
            event_id = record.event.event_id
            event_by_event_id[event_id] = record.event
            if event_id not in record_fields_by_event_id:
                record_fields_by_event_id[event_id] = set()
            if record.source == SOURCE_SELECT_MENU:
                for record_field in record.record:
                    if record_field not in valid_select_menu_option_names:
                        continue
                    record_fields_by_event_id[event_id].add(record_field)
            if record.source == SOURCE_MODAL:
                for record_field in record.record:
                    if record_field not in valid_custom_modal_fields_names:
                        continue
                    record_fields_by_event_id[event_id].add(record_field)
            if len(record_fields_by_event_id[event_id]) == 0:
                del record_fields_by_event_id[event_id]

        for event_id in record_fields_by_event_id:
            event = event_by_event_id[event_id]
            event_leaf_class = event.as_leaf_class()
            record_fields_sequence_by_event_id[event_id] = sorted(list(record_fields_by_event_id[event_id]))
            for record_field_name in record_fields_sequence_by_event_id[event_id]:
                field_names.append(f"({event_leaf_class.label}) {record_field_name}")
            event_ids_sequence.append(event_id)

        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

        column_names = [
            'Discord User Id',
            'Discord Username'
        ]

        for f_name in field_names:
            column_names.append(f"'{f_name}' Submission")
            column_names.append(f"'{f_name}' {'Latest' if only_latest else ''} submission timestamp")
            column_names.append(f"'{f_name}' Total submissions count")

        writer.writerow(column_names)

        for indexed_record_set in [indexed_records, indexed_anonymous_records]:
            is_anonymous = indexed_record_set == indexed_anonymous_records
            for user_id in indexed_record_set:

                user_records = indexed_record_set[user_id]
                any_record = user_records[list(user_records.keys())[0]][-1]
                discord_username = any_record.discord_user_name

                rows_cnt = 1 if only_latest else max(map(lambda event_id: len(user_records.get(event_id, [])), event_ids_sequence))

                first_row_cells = [
                    str(encode_discord_user_id(user_id)) + ' (ANONYMIZED)',
                    'ANONYMOUS'
                ] if is_anonymous else [
                    user_id,
                    discord_username
                ]

                for row_i in range(rows_cnt):
                    row_cells = list(first_row_cells)

                    for event_id in event_ids_sequence:
                        if event_id in user_records:
                            record_list = user_records[event_id]

                            field_seq = record_fields_sequence_by_event_id[event_id]

                            if record_list[-1].source == SOURCE_SELECT_MENU:
                                for field in field_seq:
                                    if only_latest:
                                        row_cells.append(
                                            '1' if field in record_list[-1].record else '0'
                                        )
                                        row_cells.append(record_list[-1].created_on)
                                    else:
                                        if row_i < len(record_list):
                                            row_cells.append(
                                                '1' if field in record_list[row_i].record else '0'
                                            )
                                            row_cells.append(record_list[row_i].created_on)
                                        else:
                                            row_cells.append('')
                                            row_cells.append('')

                                    row_cells.append(len(record_list))


                            if record_list[-1].source == SOURCE_MODAL:
                                for field in field_seq:
                                    if only_latest:
                                        row_cells.append(
                                            record_list[-1].record.get(field, '-')
                                        )
                                        row_cells.append(record_list[-1].created_on)
                                    else:
                                        if row_i < len(record_list):
                                            row_cells.append(
                                                record_list[row_i].record.get(field, '-')
                                            )
                                            row_cells.append(record_list[-1].created_on)
                                        else:
                                            row_cells.append('')
                                            row_cells.append('')

                                    row_cells.append(len(record_list))

                    writer.writerow(row_cells)

        return output


@admin.action(description=f'Export modal/menu submissions as CSV (only latest)')
def export_latest_submissions(modeladmin, request, queryset):
    only_latest = True
    csv_stringio = export_flow_submissions(queryset, only_latest=only_latest)
    response = HttpResponse(csv_stringio.getvalue())
    response['Content-Disposition'] = f'attachment; filename="{flow.flow_label}-{"latest" if only_latest else "all"}-submissions.csv"'
    return response


@admin.action(description=f'Export modal/menu submissions as CSV (all)')
def export_all_submissions(modeladmin, request, queryset):
    only_latest = False
    csv_stringio = export_flow_submissions(queryset, only_latest=only_latest)
    response = HttpResponse(csv_stringio.getvalue())
    response['Content-Disposition'] = f'attachment; filename="{flow.flow_label}-{"latest" if only_latest else "all"}-submissions.csv"'
    return response


class GuidedFlowAdmin(admin.ModelAdmin):
    class Meta:
        model = GuidedFlow

    search_fields = ("id", "slash_command_name", "flow_label", "channel_name", "community__name")

    autocomplete_fields = ("moderators_to_contact",)

    form = FixedWidthAutocompleteForm

    actions = [duplicate_flow, migrate_flow, export_latest_submissions, export_all_submissions]

admin.site.register(GuidedFlow, GuidedFlowAdmin)