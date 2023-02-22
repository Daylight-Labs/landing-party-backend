from rest_framework import views, status, mixins, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.serializers import OnboardingFlowCreationObjectSerializer
from api.models import OnboardingFlowCreationObject
from api.utils.onboarding_flow_utils import get_or_create_ftux_onboarding_obj, get_or_create_new_onboarding_obj
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from django.http.response import JsonResponse, HttpResponseNotFound, HttpResponseServerError, HttpResponse
from rest_framework.decorators import action
import asyncio
import requests
import os
import time
import json

from api.models import GuidedFlow, ShowCaptcha, GuidedFlowStepButton, GuidedFlowStep, \
    ShowCustomModal, CustomModalField, Community, GrantRole, FaqBotCreationObject

bot_token = os.environ.get('DISCORD_BOT_TOKEN')

class IsCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        if view.action == 'list':
            return True
        return obj.creator == request.user

class OnboardingFlowCreationObjectViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet):
    
    permission_classes = [IsCreator]
    serializer_class = OnboardingFlowCreationObjectSerializer
    queryset = OnboardingFlowCreationObject.objects.all()

    def list(self, request, *args, **kwargs):
        objects = OnboardingFlowCreationObject.objects.filter(creator=request.user, flow__isnull=False)
        serializer = OnboardingFlowCreationObjectSerializer(objects, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def export_csv_submissions(self, request, *args, **kwargs):
        from api.admin.guided_flow_admin import export_flow_submissions

        object = self.get_object()

        flow = object.flow

        queryset = GuidedFlow.objects.filter(id=flow.id)

        only_latest = False
        csv_stringio = export_flow_submissions(queryset, only_latest=only_latest)
        print(csv_stringio)
        print(dir(csv_stringio))
        response = HttpResponse(csv_stringio.getvalue())
        response['Content-Disposition'] = \
            f'attachment; filename="{flow.flow_label}-{"latest" if only_latest else "all"}-submissions.csv"'
        return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ftux_onboarding_obj(request):
    user = request.user

    obj = get_or_create_ftux_onboarding_obj(user)

    serializer = OnboardingFlowCreationObjectSerializer(obj)

    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_new_onboarding_obj(request):
    user = request.user

    obj = get_or_create_new_onboarding_obj(user)

    serializer = OnboardingFlowCreationObjectSerializer(obj)

    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def does_guild_have_onboarding_flow(request, id):
    guild_id = id

    label = f"onboarding-{guild_id}" \
                if GuidedFlow.objects.filter(flow_label="onboarding", community__guild_id=guild_id).exists() or \
                   GuidedFlow.objects.filter(channel_name="onboarding", community__guild_id=guild_id).exists() \
                else f"onboarding"

    if GuidedFlow.objects.filter(flow_label=label, community__guild_id=guild_id).exists() or \
       GuidedFlow.objects.filter(channel_name=label, community__guild_id=guild_id).exists():
        onboarding_exists = True
    else:
        onboarding_exists = False

    return JsonResponse({
        "onboarding_exists": onboarding_exists,
        "guild_id": guild_id
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_channels(request, guild_id):
    response = requests.get(f'https://discord.com/api/v10/guilds/{guild_id}/channels', headers={'Authorization': f'Bot {bot_token}'})
    if response.status_code == 200:
        return JsonResponse(response.json(), safe=False)
    else:
        return JsonResponse(status=response.status_code, data=response.json(), safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_roles(request, guild_id):
    response = requests.get(f'https://discord.com/api/v10/guilds/{guild_id}/roles', headers={'Authorization': f'Bot {bot_token}'})
    if response.status_code == 200:
        return JsonResponse(response.json(), safe=False)
    else:
        return JsonResponse(status=response.status_code, data=response.json())

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def does_bot_have_expected_guild_permissions(request, id):
    is_faq = request.GET.get('is_faq')

    creation_obj = None
    model = FaqBotCreationObject if is_faq else OnboardingFlowCreationObject
    try:
        creation_obj = model.objects.get(pk=id)
    except:
        return HttpResponseNotFound()

    if creation_obj.guild_id is None:
        return JsonResponse(status=400, data={"error": "guild id is not set"})


    response = requests.get(f'https://discord.com/api/v10/guilds/{creation_obj.guild_id}', headers={'Authorization': f'Bot {bot_token}'})

    if response.status_code != 200:
        return JsonResponse(status=response.status_code, data=response.json())

    response_data = response.json()
    client_id = os.environ.get('DISCORD_CLIENT_ID')
    permission = None
    for role in response_data["roles"]:
        tags = role.get("tags")
        if tags:
            bot_id = tags.get("bot_id")
            print(f"Bot ID: {bot_id}")
            print(f"Client ID: {client_id}")
            if bot_id and bot_id == client_id:
                permission = int(role.get("permissions"))

    # ADMIN_PERMISSIONS
    view_channel_permission = 1 << 3
    if (permission & view_channel_permission) == view_channel_permission:
        return JsonResponse({"has_permissions":True})
    
    # KICK_MEMBERS
    view_channel_permission = 1 << 1
    if not (permission & view_channel_permission) == view_channel_permission:
        return JsonResponse(status=400, data={"error": "KICK_MEMBERS permission is not granted"})
    
    # ADD_REACTIONS
    view_channel_permission = 1 << 6
    if not (permission & view_channel_permission) == view_channel_permission:
        return JsonResponse(status=400, data={"error": "ADD_REACTIONS permission is not granted"})

    # VIEW_CHANNEL
    view_channel_permission = 1 << 10
    if not (permission & view_channel_permission) == view_channel_permission:
        return JsonResponse(status=400, data={"error": "VIEW_CHANNEL permission is not granted"})
    
    # SEND_MESSAGES
    view_channel_permission = 1 << 11
    if not (permission & view_channel_permission) == view_channel_permission:
        return JsonResponse(status=400, data={"error": "SEND_MESSAGES permission is not granted"})
    
    # EMBED_LINKS
    view_channel_permission = 1 << 14
    if not (permission & view_channel_permission) == view_channel_permission:
        return JsonResponse(status=400, data={"error": "EMBED_LINKS permission is not granted"})
    
    # ATTACH_FILES
    view_channel_permission = 1 << 15
    if not (permission & view_channel_permission) == view_channel_permission:
        return JsonResponse(status=400, data={"error": "ATTACH_FILES permission is not granted"})
    
    # MANAGE_ROLES
    view_channel_permission = 1 << 28
    if not (permission & view_channel_permission) == view_channel_permission:
        return JsonResponse(status=400, data={"error": "MANAGE_ROLES permission is not granted"})
    
    # MANAGE_THREADS
    view_channel_permission = 1 << 34
    if not (permission & view_channel_permission) == view_channel_permission:
        return JsonResponse(status=400, data={"error": "MANAGE_THREADS permission is not granted"})

    # CREATE_PUBLIC_THREADS
    view_channel_permission = 1 << 35
    if not (permission & view_channel_permission) == view_channel_permission:
        return JsonResponse(status=400, data={"error": "CREATE_PUBLIC_THREADS permission is not granted"})
    
    # CREATE_PRIVATE_THREADS
    view_channel_permission = 1 << 36
    if not (permission & view_channel_permission) == view_channel_permission:
        return JsonResponse(status=400, data={"error": "CREATE_PRIVATE_THREADS permission is not granted"})

    # SEND_MESSAGES_IN_THREADS
    view_channel_permission = 1 << 38
    if not (permission & view_channel_permission) == view_channel_permission:
        return JsonResponse(status=400, data={"error": "SEND_MESSAGES_IN_THREADS permission is not granted"})

    return JsonResponse({"has_permissions":True})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def does_bot_have_expected_channel_permissions(request, id):

    override_channel_id = request.GET.get('channel_id')

    onboarding_flow = None
    try:
        onboarding_flow = OnboardingFlowCreationObject.objects.get(pk=id)
    except:
        return HttpResponseNotFound()
    
    if onboarding_flow.guild_id is None:
        return JsonResponse(status=400, data={"error": "guild id is not set"})

    if override_channel_id is None and onboarding_flow.channel_id is None:
        return JsonResponse(status=400, data={"error": "channel id is not set"})
    
    client_id = os.environ.get('DISCORD_CLIENT_ID')
    role_response = requests.get(f'https://discord.com/api/v10/guilds/{onboarding_flow.guild_id}/roles', headers={'Authorization': f'Bot {bot_token}'})
    if role_response.status_code != 200:
        return JsonResponse(status=role_response.status_code, data=role_response.json())
    role_response_data = role_response.json()

    role_id_for_bot = None
    for role in role_response_data:
        tags = role.get("tags")
        if tags:
            bot_id = tags.get("bot_id")
            if bot_id and bot_id == client_id:
                role_id_for_bot = role.get("id")
    if role_id_for_bot is None:
        return JsonResponse(status=400, data={"error": "Role for bot doesn't exist"})

    channel_id = override_channel_id if override_channel_id else onboarding_flow.channel_id

    channel_response = requests.get(f'https://discord.com/api/v10/channels/{channel_id}', headers={'Authorization': f'Bot {bot_token}'})
    if channel_response.status_code != 200:
        return JsonResponse(status=channel_response.status_code, data=channel_response.json())
    channel_response_data = channel_response.json()
    permission_overwrites = channel_response_data.get("permission_overwrites")
    
    if not permission_overwrites:
        return JsonResponse({"has_permissions":True})

    bot_permission_overwrite = next((p for p in permission_overwrites if p.get("id") == role_id_for_bot), None)
    if bot_permission_overwrite:
        deny_permissions = int(bot_permission_overwrite.get("deny"))
        if deny_permissions != 0:
            return JsonResponse({"has_permissions":False})

    # TODO check if @everyone role overwrite affects bot
    # everyone_role_id = onboarding_flow.guild_id
    # bot_permission_overwrite = next((p for p in permission_overwrites if str(p.get("id")) == str(onboarding_flow.guild_id)), None)
    # if bot_permission_overwrite:
    #     deny_permissions = int(bot_permission_overwrite.get("deny"))
    #     if deny_permissions != 0:
    #         return JsonResponse({"has_permissions": False})

    return JsonResponse({"has_permissions":True})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_flow_and_permanent_embed(request, id):
    onboarding_flow = None
    try:
        onboarding_flow = OnboardingFlowCreationObject.objects.get(pk=id)
    except:
        return HttpResponseNotFound()

    if onboarding_flow.flow:
        return JsonResponse(status=400, data={"error": "This flow already exists"})

    captcha = onboarding_flow.captcha
    channel_id = onboarding_flow.channel_id
    role_id = onboarding_flow.role_id
    guild_id = onboarding_flow.guild_id

    if guild_id is None or channel_id is None or role_id is None or guild_id is None:
        return JsonResponse(status=400, data={"error": "Captcha, channel id, role id and guild id must not be null"})
    
    community = None
    try:
        community = Community.objects.get(guild_id=guild_id)
    except:
        community = Community.objects.create(guild_id=guild_id)

    community.admins.add(request.user)

    url = f'https://discord.com/api/v10/guilds/{guild_id}'
    response = requests.get(url, headers={'Authorization': f'Bot {bot_token}'})

    if response.status_code != 200:
        return JsonResponse(status=response.status_code, data=response.json())
    response_data = response.json()

    community.name = response_data['name']
    community.save()


    label = f"onboarding-{community.guild_id}" \
                if GuidedFlow.objects.filter(flow_label="onboarding", community=community).exists() or \
                   GuidedFlow.objects.filter(channel_name="onboarding", community=community).exists() \
                else f"onboarding"

    if GuidedFlow.objects.filter(flow_label=label).exists() or \
            GuidedFlow.objects.filter(channel_name=label).exists():
        return JsonResponse(status=400, data={"error": "Onboarding flow already exists"})

    guided_flow = GuidedFlow.objects.create(
        community=community,
        flow_label=label,
        channel_name=label,
        is_ephemeral=True)

    custom_modal = ShowCustomModal.objects.create(title="Question Title")
    if onboarding_flow.question_1:
        CustomModalField.objects.create(modal=custom_modal, label=onboarding_flow.question_1, required=onboarding_flow.question_1_required)
    if onboarding_flow.question_2:
        CustomModalField.objects.create(modal=custom_modal, label=onboarding_flow.question_2, required=onboarding_flow.question_2_required)
    if onboarding_flow.question_3:
        CustomModalField.objects.create(modal=custom_modal, label=onboarding_flow.question_3, required=onboarding_flow.question_3_required)
    if onboarding_flow.question_4:
        CustomModalField.objects.create(modal=custom_modal, label=onboarding_flow.question_4, required=onboarding_flow.question_4_required)
    if onboarding_flow.question_5:
        CustomModalField.objects.create(modal=custom_modal, label=onboarding_flow.question_5, required=onboarding_flow.question_5_required)
    
    if captcha == OnboardingFlowCreationObject.CaptchaType.NONE.value:
        guided_flow.triggered_handlers.add(custom_modal)
    else:
        captcha_step = ShowCaptcha()
        if captcha == OnboardingFlowCreationObject.CaptchaType.MATH.value:
            captcha_step.captcha_type = ShowCaptcha.CaptchaType.MATH
        elif captcha == OnboardingFlowCreationObject.CaptchaType.TEXT.value:
            captcha_step.captcha_type = ShowCaptcha.CaptchaType.TEXT
        captcha_step.save()

        captcha_completed_step = GuidedFlowStep.objects.create(step_text="Successfully completed captcha", guided_flow=guided_flow)
        captcha_completed_step_button = GuidedFlowStepButton.objects.create(button_label="Continue", button_style=1, flow_step=captcha_completed_step)
        guided_flow.triggered_handlers.add(captcha_step)
        captcha_step.triggered_handlers.add(captcha_completed_step)
        captcha_completed_step_button.triggered_handlers.add(custom_modal)

    
    finished_flow_step = GuidedFlowStep.objects.create(step_text="Flow is finished", guided_flow=guided_flow)
    grant_role_step = GrantRole.objects.create(granted_role_id=role_id)
    custom_modal.triggered_handlers.add(finished_flow_step)
    custom_modal.triggered_handlers.add(grant_role_step)
    
    onboarding_flow.flow = guided_flow
    onboarding_flow.save()

    embedded_message_request = get_message_components_for_permanent_embed(guided_flow.event_id)
    url = f'https://discord.com/api/v10/channels/{channel_id}/messages'
    response = requests.post(url, json = embedded_message_request, headers={'Authorization': f'Bot {bot_token}'})

    if response.status_code != 200:
        return JsonResponse(status=response.status_code, data=response.json())
    response_data = response.json()
    onboarding_flow.permanent_embed_message_id = response_data["id"]
    onboarding_flow.permanent_embed_channel_id = response_data["channel_id"]
    onboarding_flow.save()

    return JsonResponse({"success":True})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def commit_edits(request, id):
    onboarding_flow = None
    try:
        onboarding_flow = OnboardingFlowCreationObject.objects.get(pk=id)
    except:
        return HttpResponseNotFound()
    
    guided_flow = onboarding_flow.flow
    if not guided_flow:
        return JsonResponse(status=400, data={"error": "No guided flow exists for this object"})

    captcha = onboarding_flow.captcha
    role_id = onboarding_flow.role_id
    channel_id = onboarding_flow.channel_id
    permanent_embed_message_id = onboarding_flow.permanent_embed_message_id
    permanent_embed_channel_id = onboarding_flow.permanent_embed_channel_id

    if captcha is None or role_id is None or channel_id is None:
        return JsonResponse(status=400, data={"error": "Captcha, channel id, role id and guild id must not be null"})
    
    if channel_id != permanent_embed_channel_id:
        if permanent_embed_message_id is not None and permanent_embed_channel_id is not None:
            # Delete old embed and create new embedd
            url = f'https://discord.com/api/v10/channels/{permanent_embed_channel_id}/messages/{permanent_embed_message_id}'
            response = requests.delete(url, headers={'Authorization': f'Bot {bot_token}'})
            if response.status_code != 204:
                return JsonResponse(status=response.status_code, data=response.json())
        
        embedded_message_request = get_message_components_for_permanent_embed(guided_flow.event_id)
        url = f'https://discord.com/api/v10/channels/{channel_id}/messages'
        response = requests.post(url, json = embedded_message_request, headers={'Authorization': f'Bot {bot_token}'})

        if response.status_code != 200:
            return JsonResponse(status=response.status_code, data=response.json())
        response_data = response.json()
        onboarding_flow.permanent_embed_message_id = response_data["id"]
        onboarding_flow.permanent_embed_channel_id = response_data["channel_id"]
        onboarding_flow.save()
        
    
    first_step = guided_flow.triggered_handlers.first()
    if not first_step:
        # TODO: Add Sentry exception for invalid state
        return HttpResponseServerError()
    
    try:
        captcha_step = ShowCaptcha.objects.get(event_handler_id=first_step.event_handler_id)
        captcha_completed_step = captcha_step.triggered_handlers.first()
        captcha_completed_step = GuidedFlowStep.objects.get(event_handler_id=captcha_completed_step.event_handler_id)
        custom_modal_step = captcha_completed_step.step_buttons.first().triggered_handlers.first()
        custom_modal_step = ShowCustomModal.objects.get(event_handler_id=custom_modal_step.event_handler_id)
        
        role_granting_step = None
        for s in custom_modal_step.triggered_handlers.all():
            try:
                role_granting_step = GrantRole.objects.get(event_handler_id=s.event_handler_id)
                role_granting_step.granted_role_id = role_id
                role_granting_step.save()
            except:
                pass

        # TODO: This is the case where the current flow is captcha and modal

        if captcha == OnboardingFlowCreationObject.CaptchaType.NONE.value:
            # Delete Captcha Step
            captcha_step.delete()
            captcha_completed_step.delete()
            guided_flow.triggered_handlers.all().delete()
            guided_flow.triggered_handlers.add(custom_modal_step)

            # Update custom modal questions
            update_custom_modal_questions(custom_modal_step, onboarding_flow)
            return JsonResponse({"success":True})
        else:
            # Update custom modal questions and captcha type
            update_captcha(captcha_step, onboarding_flow)
            update_custom_modal_questions(custom_modal_step, onboarding_flow)
            return JsonResponse({"success":True})
    except:
        pass

    try:
        custom_modal_step = ShowCustomModal.objects.get(event_handler_id=first_step.event_handler_id)

        role_granting_step = None
        for s in custom_modal_step.triggered_handlers.all():
            try:
                role_granting_step = GrantRole.objects.get(event_handler_id=s.event_handler_id)
                role_granting_step.granted_role_id = role_id
                role_granting_step.save()
            except:
                pass

        # TODO: This is the case where the current flow is only modal

        if captcha == OnboardingFlowCreationObject.CaptchaType.NONE.value:
            update_custom_modal_questions(custom_modal_step, onboarding_flow)
            return JsonResponse({"success":True})
        else:
            # Add captcha step
            captcha_step = ShowCaptcha()
            if captcha == OnboardingFlowCreationObject.CaptchaType.MATH.value:
                captcha_step.captcha_type = ShowCaptcha.CaptchaType.MATH
            elif captcha == OnboardingFlowCreationObject.CaptchaType.TEXT.value:
                captcha_step.captcha_type = ShowCaptcha.CaptchaType.TEXT
            captcha_step.save()
            captcha_completed_step = GuidedFlowStep.objects.create(step_text="Successfully completed captcha", guided_flow=guided_flow)
            captcha_completed_step_button = GuidedFlowStepButton.objects.create(button_label="Continue", button_style=1, flow_step=captcha_completed_step)
            guided_flow.triggered_handlers.remove(custom_modal_step)
            guided_flow.triggered_handlers.add(captcha_step)
            captcha_step.triggered_handlers.add(captcha_completed_step)
            captcha_completed_step_button.triggered_handlers.add(custom_modal_step)
            update_captcha(captcha_step, onboarding_flow)
            update_custom_modal_questions(custom_modal_step, onboarding_flow)
            return JsonResponse({"success":True})
    except:
        return HttpResponseServerError()

def update_captcha(captcha_step: ShowCaptcha, onboarding_flow :OnboardingFlowCreationObject):
    if onboarding_flow.captcha == OnboardingFlowCreationObject.CaptchaType.MATH.value:
            captcha_step.captcha_type = ShowCaptcha.CaptchaType.MATH
    elif onboarding_flow.captcha == OnboardingFlowCreationObject.CaptchaType.TEXT.value:
        captcha_step.captcha_type = ShowCaptcha.CaptchaType.TEXT
    captcha_step.save()

def update_custom_modal_questions(custom_modal_step: ShowCustomModal, onboarding_flow :OnboardingFlowCreationObject):
    custom_modal_step.fields.all().delete()
    if onboarding_flow.question_1:
        CustomModalField.objects.create(modal=custom_modal_step, label=onboarding_flow.question_1, required=onboarding_flow.question_1_required)
    if onboarding_flow.question_2:
        CustomModalField.objects.create(modal=custom_modal_step, label=onboarding_flow.question_2, required=onboarding_flow.question_2_required)
    if onboarding_flow.question_3:
        CustomModalField.objects.create(modal=custom_modal_step, label=onboarding_flow.question_3, required=onboarding_flow.question_3_required)
    if onboarding_flow.question_4:
        CustomModalField.objects.create(modal=custom_modal_step, label=onboarding_flow.question_4, required=onboarding_flow.question_4_required)
    if onboarding_flow.question_5:
        CustomModalField.objects.create(modal=custom_modal_step, label=onboarding_flow.question_5, required=onboarding_flow.question_5_required)
    
def get_message_components_for_permanent_embed(event_id):
    custom_id = f"EVENT_TYPE_EVENT, {event_id},0,[]"
    embedded_message_request = {
        "embeds": [{
            "title": "Verifcation Required",
            "description": "To gain access you need to prove you are a human by completing a captcha. Click the button below to get started!",
            "color": 3447003
        }],
        "components": [{
            "type": 1,
            "components": [{
                "type": 2,
                "label": "Begin",
                "style": 1,
                "custom_id": custom_id
            }]
        }]
    }
    return embedded_message_request