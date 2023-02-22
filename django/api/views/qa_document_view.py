from api.serializers import QaDocumentSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, SAFE_METHODS, BasePermission
from rest_framework import views, status, mixins, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from django.http.response import JsonResponse
from django.db.models import Q

import json

from datetime import datetime
from api.models.qa_document import QaDocument
from api.models.unanswered_question import UnansweredQuestion
from api.models.community import Community
from api.models.tag import Tag
from api.utils.const import TRUE_VALUES

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UpdateQaDocumentPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return not request.user.is_anonymous and request.user.is_managed_community(obj.guild_id)

class QaDocumentViewSet(mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet,
                        UpdateQaDocumentPermission):

    serializer_class = QaDocumentSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticatedOrReadOnly, UpdateQaDocumentPermission]

    def list(self, request, *args, **kwargs):
        search = request.GET.get('search', '')
        tokens = search.split(' ')
        condition = Q(prompt__isnull=False)
        for token in tokens:
            condition = condition & (Q(prompt__icontains=token) | Q(completion__icontains=token))
        qa_documents = self.get_queryset()
        qa_documents = qa_documents.filter(condition)
        page = self.paginate_queryset(qa_documents)
        if page is not None:
            serializer = QaDocumentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = QaDocumentSerializer(users, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        request = self.request
        user = request.user
        q = QaDocument.objects.all()

        guild_id = request.GET.get('guild_id')
        guild_slug = request.GET.get('guild_slug')
        tag_id = request.GET.get('tag_id')

        community = None

        if guild_id is not None:
            community = Community.objects.filter(guild_id=guild_id).first()
            q = QaDocument.objects.filter(guild_id=guild_id)

        if guild_slug is not None:
            community = Community.objects.filter(slug=guild_slug).first()

            if community is None:
                return JsonResponse({"success": False, "error": "Community not found"},
                                    status=status.HTTP_404_NOT_FOUND)

            q = QaDocument.objects.filter(guild_id=community.guild_id)

        if tag_id is not None:
            q = q.filter(tags__id=tag_id)

        if user.is_anonymous:
            q = q.filter(is_public=True)
        # PATCH/DELETE methods are managed by UpdateQaDocumentPermission
        elif request.method == 'GET' and not user.is_managed_community(community.guild_id):
            q = q.filter(is_public=True)

        q = q.order_by('-created_on')

        return q

    def create(self, request, *args, **kwargs):
        prompt = request.data['prompt']
        completion = request.data['completion']
        guild_id = request.data['guild_id']
        is_public = request.data.get('is_public')

        tag_ids = request.data.get('tag_ids')

        user = request.user

        print(f"Tassi 1 {guild_id} {is_public}")
        if not user.is_managed_community(guild_id):
            return JsonResponse({"success": False, "error": "Invalid guild_id"},
                                status=status.HTTP_404_NOT_FOUND)
        print("Tassi 2")
        qa_document = QaDocument(guild_id=guild_id,
                                 prompt=prompt,
                                 completion=completion)
        print("Tassi 3")
        if is_public is not None:
            qa_document.is_public = is_public in TRUE_VALUES
        print("Tassi 4")
        qa_document.asked_by = user
        qa_document.answered_by = user
        if tag_ids is not None:
            tags = Tag.objects.filter(id__in=tag_ids)
            qa_document.tags.set(tags)

        qa_document.update_embedding_for_prompt()

        qa_document.save()

        # TODO WIP unanswered questions
        # unanswered_questions = UnansweredQuestion.objects.filter(guild_id=managed_community.value.guild_id,
        #                                                          prompt=prompt)
        #
        # for q in unanswered_questions:
        #     q.deleted_on = datetime.now()
        #     q.save()

        serializer = QaDocumentSerializer(qa_document)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        doc_idx = self.kwargs['pk']
        prompt = request.data.get('prompt')
        completion = request.data.get('completion')
        is_public = request.data.get('is_public')

        tag_ids = request.data.get('tag_ids')

        user = request.user
        managed_communities = user.get_managed_communities()

        if len(managed_communities) is None:
            return JsonResponse({"success": False, "error": "User does not have managed community"},
                                status=status.HTTP_404_NOT_FOUND)

        qa_document_to_modify = QaDocument.objects.filter(id=doc_idx).first()

        if qa_document_to_modify is None or not user.is_managed_community(qa_document_to_modify.guild_id):
            return JsonResponse({"success": False, "error": "QA doc does not exist"},
                                status=status.HTTP_404_NOT_FOUND)

        update_last_edited_by = False
        if prompt is not None and qa_document_to_modify.prompt != prompt:
            qa_document_to_modify.prompt = prompt
            update_last_edited_by = True
        if completion is not None and qa_document_to_modify.completion != completion:
            qa_document_to_modify.completion = completion
            qa_document_to_modify.update_embedding_for_prompt()
            update_last_edited_by = True
        if is_public is not None:
            qa_document_to_modify.is_public = is_public in TRUE_VALUES
        if update_last_edited_by:
            qa_document_to_modify.last_edited_by = user
        if tag_ids is not None:
            tags = Tag.objects.filter(id__in=tag_ids)
            qa_document_to_modify.tags.set(tags, clear=True)
        qa_document_to_modify.save()

        # TODO WIP unanswered questions
        # unanswered_questions = UnansweredQuestion.objects.filter(guild_id=managed_community.value.guild_id,
        #                                                          prompt=prompt)

        # for q in unanswered_questions:
        #     q.deleted_on = datetime.now()
        #     q.save()

        serializer = QaDocumentSerializer(qa_document_to_modify)

        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        doc_idx = self.kwargs['pk']

        user = request.user
        managed_communities = user.get_managed_community()

        if len(managed_communities) == 0:
            return JsonResponse({"success": False, "error": "User does not have managed community"},
                                status=status.HTTP_404_NOT_FOUND)

        qa_document_to_delete = QaDocument.objects.filter(id=doc_idx).first()

        if qa_document_to_delete is None or not user.is_managed_community(qa_document_to_delete.guild_id):
            return JsonResponse({"success": False, "error": "QA doc does not exist"},
                                status=status.HTTP_404_NOT_FOUND)

        qa_document_to_delete.deleted_on = datetime.now()
        qa_document_to_delete.save()

        return JsonResponse({"success": True})