from api.serializers import QaDocumentSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, SAFE_METHODS
from rest_framework import views, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from django.http.response import JsonResponse

from datetime import datetime
from api.models.qa_document import QaDocument
from api.models.unanswered_question import UnansweredQuestion
from api.models import Community
from api.utils.const import TRUE_VALUES

@api_view(['GET'])
def get_community_by_slug(request):
    guild_slug = request.GET['guild_slug']

    community = Community.objects.filter(slug=guild_slug).first()

    if community is None:
        return JsonResponse({"success": False, "error": "Community not found"},
                            status=status.HTTP_404_NOT_FOUND)

    print(f"Tassi get community {community.guild_id}")
    return JsonResponse({
        "guild_id": str(community.guild_id), 
        "guild_slug": community.slug,
        "display_name": community.name,
    })