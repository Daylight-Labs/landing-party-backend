from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models

# TODO WIP
class UnansweredQuestion(TimeStampedDeletableModel):
    id = models.AutoField(primary_key=True)

    guild_id = models.BigIntegerField(db_index=True)

    prompt =  models.TextField(blank=False)

    user_id = models.BigIntegerField(db_index=True)
