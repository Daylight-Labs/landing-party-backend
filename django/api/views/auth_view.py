from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http.response import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import requests
import json
import os

from api.models import User, QaDocument, Community, UserRoleSet

from api.serializers import UserSerializer, OnboardingFlowCreationObjectSerializer
from api.utils.onboarding_flow_utils import get_or_create_ftux_onboarding_obj

DISCORD_CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET')

@api_view(['POST'])
def login_with_discord_code(request):
    last_guild_slug = request.data.get('lastGuildSlug', '')
    discord_auth_code = request.data['code']

    url = "https://discord.com/api/v8/oauth2/token"
    
    redirect_uri = None
    if settings.ENVIRONMENT == "prod":
        redirect_uri = f"https%3A%2F%2Fapp.landing.party%2Fdiscord_login_callback"
    elif settings.ENVIRONMENT == "staging":
        redirect_uri = f"https%3A%2F%2Fstaging-app.landing.party%2Fdiscord_login_callback"
    else:
        redirect_uri = f"http%3A%2F%2Flocalhost%3A3000%2Fdiscord_login_callback"

    payload = f"client_id={DISCORD_CLIENT_ID}&client_secret={DISCORD_CLIENT_SECRET}&grant_type=authorization_code&code={discord_auth_code}&redirect_uri={redirect_uri}"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache"
    }
    response = requests.request("POST", url, data=payload, headers=headers)

    if response.status_code != 200:
        print("RESPONSE DATA", response.text)
        return JsonResponse({"success": False, "message": "Invalid Discord Authorization Code"})

    access_token = json.loads(response.text)['access_token']


    url = "https://discord.com/api/v8/users/@me"
    headers = {
        'Authorization': f"Bearer {access_token}",
        'Cache-Control': "no-cache"
    }
    response = requests.request("GET", url, headers=headers)

    if response.status_code != 200:
        JsonResponse({"success": False, "message": "Couldn't get user data from discord API"})

    user_data = json.loads(response.text)

    user_id = user_data['id']
    username = user_data['username']
    avatar_hash = user_data['avatar']

    existing_user = User.objects.filter(discord_user_id=user_id).first()

    if existing_user is None:
        current_user = User.objects.create(
            discord_user_id=user_id,
            discord_username=username,
            discord_avatar_hash=avatar_hash,
            is_active=True,
            email=None
        )
    else:
        existing_user.is_active = True
        if existing_user.discord_username != username or existing_user.discord_avatar_hash != avatar_hash:
            existing_user.discord_username = username
            existing_user.discord_avatar_hash = avatar_hash
        existing_user.save()
        current_user = existing_user

    url = "https://discord.com/api/v8/users/@me/guilds"
    response = requests.request("GET", url, headers=headers)

    guild_ids = list(map(lambda x: x['id'], json.loads(response.text)))

    guilds_with_admin_role = list(Community.objects.filter(guild_id__in=guild_ids).filter(
        admin_role_ids__isnull=False
    ).exclude(
        admin_role_ids__exact=""
    ))

    guilds_with_admin_role = sorted(guilds_with_admin_role, key=lambda x: 0 if x.slug == last_guild_slug else 1)

    discord_api_too_many_requests = False

    explicit_admin_guild_ids = list(map(lambda x: x.guild_id, current_user.community_set.all()))

    # Check max 3 guilds to avoid 429 too many requests
    for guild in guilds_with_admin_role[:3]:
        guild_id = guild.guild_id

        if guild_id in explicit_admin_guild_ids:
            continue

        url = f"https://discord.com/api/v8/users/@me/guilds/{guild_id}/member"
        response = requests.request("GET", url, headers=headers)

        if response.status_code == 429:
            discord_api_too_many_requests = True
            break

        role_ids = json.loads(response.text)['roles']

        roleset = UserRoleSet.objects.filter(
            community__guild_id=guild_id,
            user=current_user
        ).first()

        if roleset is None:
            UserRoleSet.objects.create(
                community=Community.objects.get(guild_id=guild_id),
                user=current_user,
                role_ids=role_ids
            )
        else:
            roleset.role_ids = role_ids
            roleset.save()

    refresh = RefreshToken.for_user(current_user)

    obj = get_or_create_ftux_onboarding_obj(current_user)

    serializer = OnboardingFlowCreationObjectSerializer(obj)

    return JsonResponse({"success": True,
                         "discord_access_token": access_token,
                         "refresh": str(refresh),
                         "access": str(refresh.access_token),
                         "discord_user_id": str(current_user.discord_user_id),
                         "discord_username": current_user.discord_username,
                         "discord_avatar_hash": current_user.discord_avatar_hash,
                         "show_onboarding_flow_ftux": obj.flow is None,
                         "onboarding_flow_object": serializer.data,
                         "discord_api_too_many_requests": discord_api_too_many_requests
                         }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    user = request.user
    if user is None or user.is_anonymous:
        return JsonResponse({"success": False, "error": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)

    serializer = UserSerializer(user)

    return Response(serializer.data)