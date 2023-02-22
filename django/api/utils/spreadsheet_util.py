import gspread
import os
import json
import io
import csv
from datetime import datetime, timedelta

def upload_csv_to_google_spreadsheet(csv_string, spreadsheet_id):
    credentials = json.loads(os.environ['GOOGLE_CLOUD_SERVICE_ACCOUNT_KEY'])

    gc = gspread.service_account_from_dict(credentials)

    gc.import_csv(spreadsheet_id, data=csv_string)

def export_faq_bot_stats_to_csv(guild_id):
    from django.db.models import Count, F
    from api.models import QaDocument, User
    from api.models.event_log import EVENT_TYPE_QUESTION_WITH_DIRECT_ANSWER

    stats_by_user_id_by_question = {}

    qa_doc_prompt_by_id = {}

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

    for qa_doc in QaDocument.objects.filter(guild_id=guild_id):
        qa_doc_prompt_by_id[qa_doc.id] = qa_doc.prompt
        for row in qa_doc.related_event_logs.filter(type=EVENT_TYPE_QUESTION_WITH_DIRECT_ANSWER)\
                        .values('triggered_by_user__discord_user_id') \
                        .order_by('triggered_by_user__discord_user_id') \
                        .annotate(total=Count('triggered_by_user__discord_user_id'),
                                  user_id=F('triggered_by_user__discord_user_id')):
            stats_by_user_id_by_question[row['user_id']] = stats_by_user_id_by_question.get(row['user_id'], {})
            stats_by_user_id_by_question[row['user_id']][qa_doc.id] = \
                stats_by_user_id_by_question[row['user_id']].get(qa_doc.id, {})
            stats_by_user_id_by_question[row['user_id']][qa_doc.id]['all_time_ask_count'] = row['total']

        for row in qa_doc.related_event_logs\
                        .filter(type=EVENT_TYPE_QUESTION_WITH_DIRECT_ANSWER)\
                        .filter(created_on__gte=datetime.now() - timedelta(days=7)) \
                        .values('triggered_by_user__discord_user_id') \
                        .order_by('triggered_by_user__discord_user_id') \
                        .annotate(total=Count('id'),
                                  user_id=F('triggered_by_user__discord_user_id')):
            stats_by_user_id_by_question[row['user_id']] = stats_by_user_id_by_question.get(row['user_id'], {})
            stats_by_user_id_by_question[row['user_id']][qa_doc.id] = \
                stats_by_user_id_by_question[row['user_id']].get(qa_doc.id, {})
            stats_by_user_id_by_question[row['user_id']][qa_doc.id]['7_days_ask_count'] = row['total']

    all_user_ids = list(stats_by_user_id_by_question.keys())
    username_by_user_id = {}
    for row in User.objects.filter(discord_user_id__in=all_user_ids):
        username_by_user_id[row.discord_user_id] = row.discord_username

    header_row = ['']
    for qa_doc_id, qa_doc_prompt in qa_doc_prompt_by_id.items():
        header_row.append('(Last 7 days) ' + qa_doc_prompt)
        header_row.append('(All time) ' + qa_doc_prompt)

    writer.writerow(header_row)

    for user_id, username in username_by_user_id.items():
        row = [f'{username} (#{user_id})']

        for qa_doc_id, _ in qa_doc_prompt_by_id.items():
            stats = stats_by_user_id_by_question[user_id].get(qa_doc_id, {})
            _7_days_ask_count = stats.get('7_days_ask_count', 0)
            _all_time_ask_count = stats.get('all_time_ask_count', 0)

            row.append(_7_days_ask_count)
            row.append(_all_time_ask_count)

        writer.writerow(row)

    return output



def run_spreadsheet_migrations():
    from api.models import GuidedFlow, ShowSelectMenu, ShowCustomModal, Community
    from api.admin.guided_flow_admin import export_flow_submissions
    from api.admin.guided_flow_step_admin import export_menu_submissions_to_csv, export_modal_submissions_to_csv

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

    errors = []


    faq_stats_count = 0
    for community in Community.objects.filter(faq_bot_google_spreadsheet_id__isnull=False).exclude(
            faq_bot_google_spreadsheet_id__exact=""):
        spreadsheet_id = community.faq_bot_google_spreadsheet_id

        try:
            csv_result = export_faq_bot_stats_to_csv(community.guild_id)
            upload_csv_to_google_spreadsheet(csv_result.getvalue(), spreadsheet_id)
            faq_stats_count += 1
        except Exception as e:
            errors.append(e)

    flow_count = 0

    for flow in GuidedFlow.objects.filter(google_spreadsheet_id__isnull=False).exclude(google_spreadsheet_id__exact=""):
        spreadsheet_id = flow.google_spreadsheet_id
        qs = GuidedFlow.objects.filter(id=flow.id)

        try:
            csv_result = export_flow_submissions(qs, only_latest=False, force_anonymized=False)
            upload_csv_to_google_spreadsheet(csv_result.getvalue(), spreadsheet_id)
            flow_count += 1
        except Exception as e:
            errors.append(e)


    for flow in GuidedFlow.objects.filter(anonymized_google_spreadsheet_id__isnull=False).exclude(anonymized_google_spreadsheet_id__exact=""):
        spreadsheet_id = flow.anonymized_google_spreadsheet_id
        qs = GuidedFlow.objects.filter(id=flow.id)

        try:
            csv_result = export_flow_submissions(qs, only_latest=False, force_anonymized=True)
            upload_csv_to_google_spreadsheet(csv_result.getvalue(), spreadsheet_id)
            flow_count += 1
        except Exception as e:
            errors.append(e)

    menu_count = 0
    for menu in ShowSelectMenu.objects.filter(google_spreadsheet_id__isnull=False).exclude(
            google_spreadsheet_id__exact=""):
        spreadsheet_id = menu.google_spreadsheet_id
        qs = ShowSelectMenu.objects.filter(id=menu.id)

        try:
            csv_result = export_menu_submissions_to_csv(qs, force_anonymized=False)
            upload_csv_to_google_spreadsheet(csv_result.getvalue(), spreadsheet_id)
            menu_count += 1
        except Exception as e:
            errors.append(e)

    for menu in ShowSelectMenu.objects.filter(anonymized_google_spreadsheet_id__isnull=False).exclude(
            anonymized_google_spreadsheet_id__exact=""):
        spreadsheet_id = menu.anonymized_google_spreadsheet_id
        qs = ShowSelectMenu.objects.filter(id=menu.id)

        try:
            csv_result = export_menu_submissions_to_csv(qs, force_anonymized=True)
            upload_csv_to_google_spreadsheet(csv_result.getvalue(), spreadsheet_id)
            menu_count += 1
        except Exception as e:
            errors.append(e)

    modal_count = 0
    for modal in ShowCustomModal.objects.filter(google_spreadsheet_id__isnull=False).exclude(
            google_spreadsheet_id__exact=""):
        spreadsheet_id = modal.google_spreadsheet_id
        qs = ShowCustomModal.objects.filter(id=modal.id)

        try:
            csv_result = export_modal_submissions_to_csv(qs, force_anonymized=False)
            upload_csv_to_google_spreadsheet(csv_result.getvalue(), spreadsheet_id)
            modal_count += 1
        except Exception as e:
            errors.append(e)

    for modal in ShowCustomModal.objects.filter(anonymized_google_spreadsheet_id__isnull=False).exclude(
            anonymized_google_spreadsheet_id__exact=""):
        spreadsheet_id = modal.anonymized_google_spreadsheet_id
        qs = ShowCustomModal.objects.filter(id=modal.id)

        try:
            csv_result = export_modal_submissions_to_csv(qs, force_anonymized=True)
            upload_csv_to_google_spreadsheet(csv_result.getvalue(), spreadsheet_id)
            modal_count += 1
        except Exception as e:
            errors.append(e)

    if len(errors) > 0:
        raise errors[0]

    return {
        "success": True,
        "flow_count": flow_count,
        "menu_count": menu_count,
        "modal_count": modal_count,
        "faq_stats_count": faq_stats_count
    }
