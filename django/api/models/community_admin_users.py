from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models

class CommunityAdminUsers(TimeStampedDeletableModel):
    discord_user_id = models.BigIntegerField(null=True, unique=True, blank=True)