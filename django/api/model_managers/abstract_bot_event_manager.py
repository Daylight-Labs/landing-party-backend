from django.db import models
from django.apps import apps

class AbstractBotEventManager(models.Manager):
    """
    Only exposes objects that have NOT been soft-deleted.
    """
    def get_queryset(self):
        return super().get_queryset().filter(guidedflowstepbutton__deleted_on__isnull=True)