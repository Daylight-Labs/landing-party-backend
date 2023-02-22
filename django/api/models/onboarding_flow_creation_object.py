from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from django.contrib.postgres.fields import ArrayField
from api.models import User, GuidedFlow

class OnboardingFlowCreationObject(TimeStampedDeletableModel):

    class CaptchaType(models.TextChoices):
        MATH = 'MA'
        TEXT = 'TE'
        NONE = 'NO'

    captcha = models.CharField(
        max_length= 2,
        choices=CaptchaType.choices,
        default=CaptchaType.NONE
    )

    channel_id = models.BigIntegerField(null=True, blank=True, unique=False)
    role_id = models.BigIntegerField(null=True, blank=True, unique=False)
    guild_id = models.BigIntegerField(null=True, blank=True, unique=False)
    permanent_embed_message_id = models.BigIntegerField(null=True, blank=True, unique=True)
    permanent_embed_channel_id = models.BigIntegerField(null=True, blank=True, unique=True)

    creator = models.ForeignKey(
        User,
        to_field="discord_user_id",
        null=True, 
        on_delete=models.SET_NULL, 
        related_name="onboarding_flow_creation_objects")
    
    flow = models.ForeignKey(
        GuidedFlow,
        null=True,
        on_delete=models.CASCADE
    )

    question_1 = models.TextField(null=True, blank=True)
    question_1_required = models.BooleanField(null=False, default=False)

    question_2 = models.TextField(null=True, blank=True)
    question_2_required = models.BooleanField(null=False, default=False)

    question_3 = models.TextField(null=True, blank=True)
    question_3_required = models.BooleanField(null=False, default=False)

    question_4 = models.TextField(null=True, blank=True)
    question_4_required = models.BooleanField(null=False, default=False)

    question_5 = models.TextField(null=True, blank=True)
    question_5_required = models.BooleanField(null=False, default=False)