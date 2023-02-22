from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from drf_writable_nested.mixins import UniqueFieldsMixin

from api.models.user import User
from api.models.qa_document import QaDocument
from api.models.tag import Tag
from api.models.event_record import EventRecord
from api.models import CaptchaRequest
from api.models import OnboardingFlowCreationObject
from api.models import FaqBotCreationObject

class UserBasicSerializer(serializers.ModelSerializer):
    discord_user_id = serializers.SerializerMethodField()

    def get_discord_user_id(self, obj):
        return str(obj.discord_user_id)

    class Meta:
        model = User
        fields = ['discord_user_id', 'discord_username', 'discord_avatar_hash']
        lookup_field = 'url_slug'

class UserSerializer(UserBasicSerializer):
    managed_communities = serializers.SerializerMethodField()

    def get_managed_communities(self, obj):
        return [
            {
                "guild_id": str(com.guild_id),
                "display_name": com.name,
                "slug": com.slug
            }
            for com
            in obj.get_managed_communities()
        ]

    class Meta:
        model = User
        fields = ['discord_user_id', 'discord_username', 'discord_avatar_hash', 'managed_communities']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            'id',
            'name'
        ]
        read_only_fields = ('id',)

class EventRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRecord
        fields = [
            'id',
            'event',
            'record',
            'source',
            'channel_id',
            'guild_id',
            'discord_user_id',
            'discord_user_name'
        ]
        read_only_fields = ('id',)

class QaDocumentSerializer(serializers.ModelSerializer):

    asked_by = UserBasicSerializer()
    answered_by = UserBasicSerializer()
    last_edited_by = UserBasicSerializer()
    tags = TagSerializer(many=True)

    class Meta:
        model = QaDocument
        fields = [
            'id',
            'prompt', 'completion',
            'created_on', 'last_modified_on',
            'asked_by', 'answered_by', 'last_edited_by',
            'is_public',
            'tags'
        ]

class CaptchaRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = CaptchaRequest
        fields = [
            'id',
            'image'
        ]

class OnboardingFlowCreationObjectSerializer(serializers.ModelSerializer):
    # IntField does not work properly with BigInteger (some bits are lost)
    guild_id = serializers.CharField(allow_null=True)
    channel_id = serializers.CharField(allow_null=True)
    role_id = serializers.CharField(allow_null=True)
    captcha = serializers.CharField(allow_null=True, allow_blank=True)

    creator_name = serializers.SerializerMethodField()
    flow_created_on = serializers.SerializerMethodField()
    flow_last_modified_on = serializers.SerializerMethodField()
    community_name = serializers.SerializerMethodField()

    def get_creator_name(self, obj):
        return obj.creator.discord_username

    def get_flow_created_on(self, obj):
        if obj.flow is None:
            return None
        return obj.flow.created_on

    def get_flow_last_modified_on(self, obj):
        if obj.flow is None:
            return None
        return obj.flow.last_modified_on

    def get_community_name(self, obj):
        if obj.flow is None:
            return None
        if obj.flow.community is None:
            return None
        return obj.flow.community.name

    class Meta:
        model = OnboardingFlowCreationObject
        fields = (
            'id',
            'captcha',
            'channel_id',
            'role_id',
            'guild_id',
            'creator',
            'flow',
            'creator_name',
            'flow_created_on',
            'flow_last_modified_on',
            'community_name',
            'created_on',
            'last_modified_on',
            'question_1',
            'question_1_required',
            'question_2',
            'question_2_required',
            'question_3',
            'question_3_required',
            'question_4',
            'question_4_required',
            'question_5',
            'question_5_required',
        )

class FaqBotCreationObjectSerializer(serializers.ModelSerializer):
    
    slug = serializers.CharField(allow_null=True)
    guild_id = serializers.CharField(allow_null=True)
    admin_role_id = serializers.CharField(allow_null=True)
    channel_ids = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)

    class Meta:
        model = FaqBotCreationObject
        fields = (
            'id',
            'slug',
            'guild_id',
            'channel_ids',
            'admin_role_id'
        )