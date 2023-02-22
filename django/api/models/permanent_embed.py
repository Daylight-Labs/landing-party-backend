from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from api.models import User, Community
from api.models.abstract_bot_event import AbstractBotEvent
from api.models.abstract_bot_event_handler import AbstractBotEventHandler


class PermanentEmbed(TimeStampedDeletableModel):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="permanent_embeds",
                                  blank=True, null=True)

    # channel_entrypoint_id is deprecated
    channel_entrypoint_id = models.BigIntegerField(null=True, unique=True, default=None, blank=True)

    channel_entrypoint_ref = models.ForeignKey('DiscordChannel', on_delete=models.SET_NULL,
                                                related_name="permanent_embeds",
                                                null=True)

    def to_json(self):
        buttons = self.embed_buttons.all()
        return {
            'community': self.community.guild_id if self.community else None,
            'channel_entrypoint_id': self.channel_entrypoint_id,
            'buttons': [x.to_json(with_triggered_handlers=True) for x in buttons],
            'attached_files': list(map(lambda x: {
                'name': x.name,
                'file': x.file.name
            }, self.attached_files.all())),
        }

    def __str__(self):
        return f"{self.channel_entrypoint_ref}"