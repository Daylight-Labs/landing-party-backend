from rest_framework import views, status, mixins, viewsets
from api.serializers import TagSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, SAFE_METHODS, BasePermission
from rest_framework.response import Response
from api.models import Tag, Community
from django.http.response import JsonResponse

class UpdateTagPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return not request.user.is_anonymous and request.user.is_managed_community(obj.community.guild_id)

class TagViewSet(mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet,
                 UpdateTagPermission):

    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, UpdateTagPermission]

    def get_queryset(self):
        request = self.request
        user = request.user
        q = Tag.objects.all()

        guild_id = request.GET.get('guild_id')
        guild_slug = request.GET.get('guild_slug')

        if request.method == 'GET' and guild_id is None and guild_slug is None:
            return Tag.objects.none()

        community = None

        if guild_id is not None:
            q = Tag.objects.filter(community__guild_id=guild_id)

        if guild_slug is not None:
            community = Community.objects.filter(slug=guild_slug).first()

            if community is None:
                return JsonResponse({"success": False, "error": "Community not found"},
                                    status=status.HTTP_404_NOT_FOUND)

            q = Tag.objects.filter(community=community)

        q = q.order_by('name')

        return q

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        guild_slug = request.data.get('guild_slug')

        community = Community.objects.filter(slug=guild_slug).first()

        if community is None:
            return JsonResponse({"success": False, "error": "Community not found"},
                                status=status.HTTP_404_NOT_FOUND)

        tag = Tag.objects.create(
            name=name,
            community=community
        )

        serializer = TagSerializer(tag)

        return Response(serializer.data)