from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from api.models import Community

class DiscordChannel(TimeStampedDeletableModel):

    channel_community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="all_discord_channels")
    channel_id = models.BigIntegerField(null=False)
    channel_name = models.TextField(null=False, default="")

    def __str__(self):
        return f"#{self.channel_name} - {self.channel_community} - {self.channel_id}"

    class Meta:
        db_table = 'api_alldiscordchanels'
        unique_together = (("channel_community", "channel_id"),)