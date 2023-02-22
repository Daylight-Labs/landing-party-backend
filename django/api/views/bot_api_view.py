from api.serializers import QaDocumentSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, SAFE_METHODS
from rest_framework import views, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.http.response import JsonResponse
from django.core.files import File
from io import BytesIO

from datetime import datetime
from api.models import AbstractBotEvent, AbstractBotEventHandler, GuidedFlowStep, PermanentEmbed, \
    DiscordMessageMapping, GuidedFlowStepUserUploadedFile, DiscordChannel, Community, GuidedFlow, \
    ShowCustomModal, ShowSelectMenu
from api.permissions.bot_api_permission import BotApiPermission
import os

import requests

from api.models import ShowCaptcha

from api.utils.spreadsheet_util import run_spreadsheet_migrations

from rest_framework.permissions import AllowAny

API_CHATBOT_AUTH_TOKEN = os.environ['CHATBOT_API_AUTH_TOKEN']

@api_view(['GET'])
@permission_classes([BotApiPermission])
def get_entry_point_events(request):
    all_events = AbstractBotEvent.objects.all()

    entry_point_events = list(filter(lambda x: x.is_entry_point() and x.is_enabled(), all_events))

    return JsonResponse(list(map(lambda x: x.to_json(with_triggered_handlers=False), entry_point_events)), safe=False)

@api_view(['POST'])
def sync_all_channels(request):
    for guild in request.data['guilds']:

        guild_id = guild['id']

        community = Community.objects.filter(guild_id=guild_id).first()

        if community is None:
            continue

        existing_channels = DiscordChannel.objects.filter(channel_community__guild_id=guild_id)

        existing_channels_by_id = {}

        for x in existing_channels:
            existing_channels_by_id[str(x.channel_id)] = x

        synced_channels = guild['channels_by_id']
        for channel_id, channel_data in synced_channels.items():
            if str(channel_id) not in existing_channels_by_id:
                DiscordChannel.objects.create(
                    channel_community=community,
                    channel_id = channel_id,
                    channel_name=channel_data['name']
                )
            else:
                existing_channel = existing_channels_by_id[str(channel_id)]
                existing_channel.channel_name = channel_data['name']
                existing_channel.deleted_on = None

        for channel in existing_channels:
            if str(channel.channel_id) not in synced_channels:
                channel.delete(hard=False)

    return JsonResponse({
        "success": True
    }, safe=False)

@api_view(['GET'])
@permission_classes([BotApiPermission])
def get_event(request, id):
    event = AbstractBotEvent.objects.get(pk=id)

    return JsonResponse(event.to_json(with_triggered_handlers=True))

@api_view(['GET'])
@permission_classes([BotApiPermission])
def get_event_handler(request, id):
    event_handler = AbstractBotEventHandler.objects.get(pk=id)
    return JsonResponse(event_handler.to_json())

@api_view(['GET'])
@permission_classes([BotApiPermission])
def get_flow_by_id(request, id):
    event_handler = GuidedFlow.objects.get(pk=id)

    return JsonResponse(event_handler.to_json(with_triggered_handlers=False))

@api_view(['GET'])
@permission_classes([BotApiPermission])
def get_flow_step(request, id):
    event_handler = GuidedFlowStep.objects.get(pk=id)
    return JsonResponse(event_handler.to_json())

@api_view(['GET'])
@permission_classes([BotApiPermission])
def get_permanent_embed(request, channel_id):
    embed = PermanentEmbed.objects.get(channel_entrypoint_ref__channel_id=channel_id)

    return JsonResponse(embed.to_json())

@api_view(['POST'])
@permission_classes([BotApiPermission])
def get_first_flow_step_in_message_id_list(request):
    message_id_list = request.data['message_id_list']
    message_mapping_by_id = {}
    print(message_id_list)
    for message_mapping in DiscordMessageMapping.objects.filter(discord_message_id__in=message_id_list):
        message_mapping_by_id[str(message_mapping.discord_message_id)] = message_mapping

    for m_id in message_id_list:
        if m_id in message_mapping_by_id:
            message_mapping = message_mapping_by_id[m_id]

            flow_step = message_mapping.flow_step

            print({
                "message_id": str(m_id),
                "flow_step": flow_step.to_json(),
                "callback_ids_sets": message_mapping.callback_ids_sets
            })

            return JsonResponse({
                "message_id": str(m_id),
                "flow_step": flow_step.to_json(),
                "callback_ids_sets": message_mapping.callback_ids_sets
            })

    return JsonResponse({"success": False}, status=404)

@api_view(['POST'])
@permission_classes([BotApiPermission])
def add_message_mapping(request, message_id):
    flow_step_id = request.data['flow_step_id']

    print(flow_step_id)

    flow_step = GuidedFlowStep.objects.get(id=flow_step_id)

    callback_ids_sets = request.data['callback_ids_sets']

    message_mapping = DiscordMessageMapping.objects.create(
        discord_message_id=message_id,
        flow_step=flow_step,
        callback_ids_sets=callback_ids_sets
    )

    print({
        "flow_step": message_mapping.flow_step.to_json(),
        "callback_ids_sets": message_mapping.callback_ids_sets
    })

    return JsonResponse({
        "flow_step": message_mapping.flow_step.to_json(),
        "callback_ids_sets": message_mapping.callback_ids_sets
    })

@api_view(['POST'])
@permission_classes([BotApiPermission])
def add_user_file_upload(request):
    filename = request.data['filename']
    file_url = request.data['file_url']
    discord_user_id = request.data['discord_user_id']
    discord_username = request.data['discord_username']
    flow_step_id = request.data['flow_step_id']

    print(file_url)

    response = requests.get(file_url)

    fp = BytesIO()
    fp.write(response.content)

    step = GuidedFlowStep.objects.get(pk=flow_step_id)

    file_obj = GuidedFlowStepUserUploadedFile.objects.create(
        name=filename,
        step=step,
        discord_user_id=discord_user_id,
        discord_username=discord_username
    )

    file_obj.file.save(
        filename,
        File(fp)
    )

    file_obj.save()

    return JsonResponse({
        "success": True
    })

@api_view(['GET'])
def run_spreadsheet_migrations_now(request):
    from api.background_tasks import background_task_run_spreadsheet_migrations_now
    background_task_run_spreadsheet_migrations_now()
    return JsonResponse("triggered", safe=False)
