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
    DiscordMessageMapping, GuidedFlowStepUserUploadedFile, DiscordChannel, Community, GuidedFlow
from api.permissions.bot_api_permission import BotApiPermission
import os
from django.db import transaction

from api.models.abstract_bot_event_handler import EVENT_HANDLER_TYPE_GUIDED_FLOW_STEP, \
    EVENT_HANDLER_TYPE_DELETE_CURRENT_THREAD, EVENT_HANDLER_TYPE_ARCHIVE_CURRENT_THREAD, \
    EVENT_HANDLER_TYPE_SHOW_TICKET_MODAL, EVENT_HANDLER_TYPE_SHOW_CUSTOM_MODAL, \
    EVENT_HANDLER_TYPE_INVITE_USERS_TO_CURRENT_THREAD, \
    EVENT_HANDLER_TYPE_INVITE_USERS_WITH_ROLE_TO_CURRENT_THREAD, \
    EVENT_HANDLER_TYPE_SHOW_SELECT_MENU, EVENT_HANDLER_TYPE_GUIDED_FLOW

import requests

@api_view(['POST'])
@permission_classes([BotApiPermission])
def import_guided_flow(request):
    event_handlers = request.data['event_handlers']

    guided_flow_obj = event_handlers[0]

    if guided_flow_obj['handler_type'] != EVENT_HANDLER_TYPE_GUIDED_FLOW:
        raise Exception('First object in array should be guided flow')

    with transaction.atomic():

        event_handler_by_id = {}

        all_nested_events = []

        guided_flow = GuidedFlow.create_from_json(guided_flow_obj)

        event_handler_by_id[guided_flow_obj['event_handler_id']] = guided_flow

        for event_handler_obj in event_handlers[1:]:
            event_handler_id = event_handler_obj['event_handler_id']
            result = AbstractBotEventHandler.from_json(event_handler_obj,
                                                       flow=guided_flow)

            event_handler = result['event_handler']
            nested_events = result['nested_events']

            event_handler_by_id[event_handler_id] = event_handler

            all_nested_events.extend(nested_events)


        for event_handler_obj in event_handlers:
            event_handler = event_handler_by_id[event_handler_obj['event_handler_id']]
            for triggered_handler_id in event_handler_obj.get('triggered_handlers_ids', []):
                triggered_handler = event_handler_by_id[triggered_handler_id]
                event_handler.triggered_handlers.add(triggered_handler)
            for triggered_handler_id in event_handler_obj.get('file_upload_triggered_handlers_ids', []):
                triggered_handler = event_handler_by_id[triggered_handler_id]
                event_handler.file_upload_triggered_handlers.add(triggered_handler)

        for nested_event in all_nested_events:
            original_json = nested_event['original_json']
            created_object = nested_event['created_object']

            for triggered_handler_id in original_json['triggered_handlers_ids']:
                triggered_handler = event_handler_by_id[triggered_handler_id]
                created_object.triggered_handlers.add(triggered_handler)

    return JsonResponse({"success": True})
