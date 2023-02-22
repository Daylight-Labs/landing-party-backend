from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class CaptchaFailuresCount(TimeStampedDeletableModel):

    discord_user_id = models.BigIntegerField(unique=True, null=False)

    failure_count = models.IntegerField(
        default=0,
        validators=[
            MaxValueValidator(3999),
            MinValueValidator(0)
        ],
        null=False
    )