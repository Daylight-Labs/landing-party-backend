from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from django.contrib.postgres.fields import ArrayField
from api.models import User, GuidedFlow

class FaqBotCreationObject(TimeStampedDeletableModel):

    slug = models.TextField(null=True, blank=True)
    guild_id = models.BigIntegerField(null=True, blank=True, unique=False)
    channel_ids = ArrayField(models.BigIntegerField(null=True, blank=True, unique=False))
    admin_role_id = models.BigIntegerField(null=True, blank=True, unique=False)

    creator = models.ForeignKey(
        User,
        to_field="discord_user_id",
        null=True, 
        on_delete=models.SET_NULL, 
        related_name="faq_bot_creation_objects")

    is_completed = models.BooleanField(null=False, default=False)