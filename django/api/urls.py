from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.conf.urls import url, include
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from api.views.auth_view import login_with_discord_code, get_user
from api.views.community_view import get_community_by_slug
from api.views.logout_view import LogOutTokenView
from api.views.qa_document_view import QaDocumentViewSet
from api.views.unanswered_question_view import get_unanswered_questions
from api.views.tag_view import TagViewSet
from api.views.onboarding_flow_creation_object_view import OnboardingFlowCreationObjectViewSet, get_ftux_onboarding_obj, \
        get_channels, get_roles, does_bot_have_expected_guild_permissions, does_bot_have_expected_channel_permissions, create_flow_and_permanent_embed, \
        commit_edits, get_new_onboarding_obj, does_guild_have_onboarding_flow
from api.views.event_record_view import EventRecordSet
from api.views.bot_api_view import get_entry_point_events, get_event, get_event_handler, get_permanent_embed, \
    add_message_mapping, get_first_flow_step_in_message_id_list, add_user_file_upload, sync_all_channels, \
    get_flow_by_id, run_spreadsheet_migrations_now
from api.views.captcha_view import create_captcha_challenge, verify_captcha_challenge
from api.views.flow_import_api_view import import_guided_flow
from api.views.faq_bot_creation_object_view import FaqBotCreationObjectViewSet, get_new_faq_bot_obj, \
    does_guild_have_faq_bot, does_bot_have_channel_access, create_community_for_faq_bot_creation_object, \
    is_slug_taken

router = DefaultRouter()

router.register(r'qa_documents', QaDocumentViewSet, basename='qa_documents')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'event_records', EventRecordSet, basename='event_records')
router.register(r'of_creation_objects', OnboardingFlowCreationObjectViewSet, basename='of_creation_objects')
router.register(r'faq_creation_objects', FaqBotCreationObjectViewSet, basename='faq_creation_objects')

urlpatterns = [
    url('^api/', include(router.urls)),

    url('^admin/', admin.site.urls),

    path('api/login_with_discord_code', login_with_discord_code, name='login_with_discord_code'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogOutTokenView.as_view(), name='logout'),

    path('api/get_user', get_user, name="get-user"),
    path('api/get_community_by_slug', get_community_by_slug, name="get-community-by-slug"),

    path('api/get_unanswered_questions', get_unanswered_questions, name="get-unanswered-questions"),

    path('api/events/entry-points', get_entry_point_events, name="get-events-entry-points"),
    path('api/events/<int:id>', get_event, name="get-event"),
    path('api/event_handlers/<int:id>', get_event_handler, name="get-event-handler"),
    path('api/permanent_embed/<int:channel_id>', get_permanent_embed, name='get-permanent-embed'),

    path('api/add_discord_message_mapping/<int:message_id>', add_message_mapping, name='get_flow_step_by_message_id'),
    path('api/get_discord_message_mapping/list', get_first_flow_step_in_message_id_list,
         name='get_first_flow_step_in_message_id_list'),
    path('api/add_user_file_upload', add_user_file_upload,
         name='add_user_file_upload'),
    path('api/sync_all_channels', sync_all_channels, name='sync_all_channels'),

    path('api/create-captcha-challenge', create_captcha_challenge, name="create_captcha_challenge"),
    path('api/verify-captcha-challenge/<int:request_id>/<int:discord_user_id>', verify_captcha_challenge, name="verify_captcha_challenge"),
    path('api/get_flow_by_id/<int:id>', get_flow_by_id, name='get_flow_by_id'),
    path('api/import_guided_flow', import_guided_flow, name='import_guided_flow'),
    path('api/run_spreadsheet_migrations_now', run_spreadsheet_migrations_now, name='run_spreadsheet_migrations_now'),

    path('api/get_ftux_onboarding_obj', get_ftux_onboarding_obj, name='get_ftux_onboarding_obj'),
    path('api/get_new_onboarding_obj', get_new_onboarding_obj, name='get_new_onboarding_obj'),

    path('api/get_channels/<int:guild_id>', get_channels, name='get_channels'),
    path('api/get_roles/<int:guild_id>', get_roles, name='get_roles'),
    path('api/onboarding/does_guild_have_onboarding_flow/<int:id>', does_guild_have_onboarding_flow, name='does_guild_have_onboarding_flow'),
    path('api/onboarding/does_bot_have_expected_guild_permissions/<int:id>', does_bot_have_expected_guild_permissions, name='does_bot_have_expected_guild_permissions'),
    path('api/onboarding/does_bot_have_expected_channel_permissions/<int:id>', does_bot_have_expected_channel_permissions, name='does_bot_have_expected_channel_permissions'),
    path('api/onboarding/create_flow_and_permanent_embed/<int:id>', create_flow_and_permanent_embed, name='create_flow_and_permanent_embed'),
    path('api/onboarding/commit_edits/<int:id>', commit_edits, name='commit_edits'),

    path('api/get_new_faq_bot_obj', get_new_faq_bot_obj, name='get_new_faq_bot_obj'),
    path('api/does_guild_have_faq_bot/<int:id>', does_guild_have_faq_bot, name='does_guild_have_faq_bot'),
    path('api/is_slug_taken/<str:slug>', is_slug_taken, name='is_slug_taken'),
    path('api/does_bot_have_channel_access/<str:channel_ids>', does_bot_have_channel_access, name='does_bot_have_channel_access'),
    path('api/create-community-for-faq_bot/<int:id>', create_community_for_faq_bot_creation_object, name='create_community_for_faq_bot_creation_object')
]
