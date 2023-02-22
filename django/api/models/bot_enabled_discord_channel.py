from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from api.models import Community

class BotEnabledDiscordChannel(TimeStampedDeletableModel):

    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="bot_enabled_discord_channels")

    # Deprecated channel_id
    channel_id = models.BigIntegerField(null=True, unique=True)

    channel_ref = models.ForeignKey('DiscordChannel', on_delete=models.SET_NULL, related_name="bot_enabled_discord_channel",
                                    null=True)

    class Meta:
        db_table = 'api_botenableddiscordchannel'

    def save(self, *args, **kwargs):
        if self.pk is None:
            existing_channels = BotEnabledDiscordChannel.objects.with_deleted().filter(community=self.community,
                                                                                       channel_ref=self.channel_ref
                                                                                      )
            if len(existing_channels) > 0:
                for existing_channel in existing_channels:
                    existing_channel.delete(hard=True)
        super(BotEnabledDiscordChannel, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} - {self.channel_ref}"