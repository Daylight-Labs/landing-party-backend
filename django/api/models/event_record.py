from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from api.models import AbstractBotEvent

class EventRecord(TimeStampedDeletableModel):

    id = models.AutoField(primary_key=True)

    event = models.ForeignKey(
        AbstractBotEvent,
        on_delete=models.SET_NULL,
        related_name="records",
        null=True)

    record = models.JSONField(null=True)

    class Source(models.TextChoices):
        MODAL = 'modal'
        SELECT_MENU = 'select-menu'

    source = models.CharField(
        max_length=25,
        choices=Source.choices,
        null=True
    )

    channel_id = models.BigIntegerField(null=True)
    guild_id = models.BigIntegerField(null=True)
    discord_user_id = models.BigIntegerField(null=True)
    discord_user_name = models.TextField(null=False, blank=True, default="")