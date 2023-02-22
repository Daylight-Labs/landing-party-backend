from rest_framework import views, status, mixins, viewsets
from rest_framework.permissions import BasePermission
from api.models import FaqBotCreationObject, Community, DiscordChannel, BotEnabledDiscordChannel
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.serializers import FaqBotCreationObjectSerializer
from rest_framework.decorators import api_view, permission_classes
from api.utils.onboarding_flow_utils import get_or_create_new_faq_bot_obj
from django.http.response import JsonResponse, HttpResponseNotFound
import requests
import os

bot_token = os.environ.get('DISCORD_BOT_TOKEN')

class IsCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        if view.action == 'list':
            return True
        return obj.creator == request.user

class FaqBotCreationObjectViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet):
    
    permission_classes = [AllowAny]
    serializer_class = FaqBotCreationObjectSerializer
    queryset = FaqBotCreationObject.objects.all()

    def list(self, request, *args, **kwargs):
        objects = FaqBotCreationObject.objects.filter(creator=request.user, flow__isnull=False)
        serializer = FaqBotCreationObject(objects, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_new_faq_bot_obj(request):
    user = request.user

    obj = get_or_create_new_faq_bot_obj(user)

    serializer = FaqBotCreationObjectSerializer(obj)

    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_community_for_faq_bot_creation_object(request, id):
    community_name = request.data['community_name']

    creation_object = None
    try:
        creation_object = FaqBotCreationObject.objects.get(pk=id)
    except:
        return HttpResponseNotFound()

    if creation_object.is_completed:
        return JsonResponse(status=400, data={"error": "There already exists a community for this creation object."})

    slug = creation_object.slug
    guild_id = creation_object.guild_id
    channel_ids = creation_object.channel_ids
    admin_role_id = creation_object.admin_role_id

    if slug is None or guild_id is None or channel_ids is None or admin_role_id is None:
        return JsonResponse(status=400, data={"error": "Slug, guild id, channel ids and admin role id must not be null"})

    community = None
    try:
        community = Community.objects.create(guild_id=guild_id, name=community_name)
    except:
        return JsonResponse(status=400, data={"error": "The community already exists"})
    
    community.slug = slug
    community.admin_role_ids = admin_role_id
    community.admins.add(request.user)

    for channel_id in channel_ids:
        try:
            channel = DiscordChannel.objects.filter(
                    channel_id=channel_id,
                ).first()
            if channel is None:
                channel = DiscordChannel.objects.create(
                    channel_community=community,
                    channel_id=channel_id,
                )
            BotEnabledDiscordChannel.objects.create(
                community=community,
                channel_id=channel_id,
                channel_ref=channel
            )
        except:
            return JsonResponse(status=400, data={"error": "Channels already exist"})

    community.save()

    creation_object.is_completed = True
    creation_object.save()

    return JsonResponse({"success":True})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def does_guild_have_faq_bot(request, id):
    guild_id = id

    community = Community.objects.filter(guild_id=guild_id).first()
    slug = None

    if community is not None:
        faq_bot_exists = True
        slug = community.slug
    else:
        faq_bot_exists = False

    return JsonResponse({
        "faq_bot_exists": faq_bot_exists,
        "guild_id": str(guild_id),
        "slug": slug
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def does_bot_have_channel_access(request, channel_ids):
    for channel_id in channel_ids.split(','):
        channel_response = requests.get(f'https://discord.com/api/v10/channels/{channel_id}', headers={'Authorization': f'Bot {bot_token}'})
        if channel_response.status_code != 200:
            return JsonResponse({"has_permissions":False})
    return JsonResponse({"has_permissions":True})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_slug_taken(request, slug):
    return JsonResponse({"is_slug_taken": Community.objects.filter(slug=slug).exists()})