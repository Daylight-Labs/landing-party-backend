from rest_framework.permissions import IsAuthenticated
from rest_framework import views, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from django.http.response import JsonResponse

from datetime import datetime
from api.models.qa_document import QaDocument
from api.models.unanswered_question import UnansweredQuestion
from api.utils.const import TRUE_VALUES
from api.serializers import QaDocumentSerializer

# WIP TODO unanswered questions
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unanswered_questions(request):
    user = request.user
    managed_community = user.get_managed_community()
    if managed_community is None:
        return JsonResponse({"success": False, "error": "User does not have managed community"},
                            status=status.HTTP_404_NOT_FOUND)

    unanswered_questions = UnansweredQuestion.objects.filter(
        guild_id=managed_community.value.guild_id,
        deleted_on__isnull=True
    )

    return JsonResponse([
        {
            "id": doc.id,
            "prompt": doc.prompt,
            "created_on": doc.created_on
        }
        for doc
        in unanswered_questions
    ], safe=False)