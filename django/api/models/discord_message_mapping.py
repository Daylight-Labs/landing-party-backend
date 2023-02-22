from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models

class DiscordMessageMapping(models.Model):
    discord_message_id = models.BigIntegerField(null=False, primary_key=True)
    flow_step = models.ForeignKey('GuidedFlowStep', on_delete=models.CASCADE, related_name="message_mappings")
    callback_ids_sets = models.JSONField()
