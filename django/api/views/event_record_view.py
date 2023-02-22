from rest_framework import views, status, mixins, viewsets
from api.serializers import EventRecordSerializer
from api.models import EventRecord
from api.permissions.bot_api_permission import BotApiPermission

class EventRecordSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):

    serializer_class = EventRecordSerializer
    queryset = EventRecord.objects.all()
    permission_classes = [BotApiPermission]
