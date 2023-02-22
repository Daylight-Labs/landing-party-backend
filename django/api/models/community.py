from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django import forms

class FloatRangeField(models.FloatField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, step=None, **kwargs):
        self.min_value, self.max_value, self.step = min_value, max_value, step
        models.FloatField.__init__(self, verbose_name, name, **kwargs)
    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value':self.max_value,
                    'widget': forms.NumberInput(attrs={'step': self.step})}
        defaults.update(kwargs)
        return super(FloatRangeField, self).formfield(**defaults)

class Community(TimeStampedDeletableModel):

    name = models.CharField(max_length=30)
    slug = models.CharField(max_length=30)
    admins = models.ManyToManyField("User")
    guild_id = models.BigIntegerField(null=True, unique=True, default=None, blank=True)

    is_active = models.BooleanField(default=True, null=False)
    minimum_threshold = FloatRangeField(default=0.9, null=False,
                                               validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                                               min_value=0, max_value=1,
                                               step=0.01
                                               )

    notifications_channel_ref = models.ForeignKey('DiscordChannel', on_delete=models.SET_NULL,
                                                  related_name="is_notification_channel_for_community",
                                                  null=True)

    admin_role_ids = models.TextField(null=True, blank=True,
                                      help_text="Comma separated role ids which will be considered admin roles by the bot")

    verified_role_id = models.BigIntegerField(null=True, blank=True, default=None)

    kick_users_who_joined_but_did_not_verify_after_days = models.IntegerField(null=False, default=3)

    kick_users_who_joined_but_did_not_verify_after_hours = models.IntegerField(null=False, default=0,
                                                                               help_text="If both days and hours are provided, they are summed up")

    kick_users_ignore_datetime_before_utc = models.DateTimeField(null=True, blank=True)

    faq_bot_google_spreadsheet_id = models.CharField(max_length=100, null=True, blank=True,
                                                     help_text="Spreadsheet ID where to export FAQ bot response stats per user")

    kick_users_who_sent_spam_times = models.IntegerField(null=True,
                                                         help_text="After user sent spam (see 'Is spam' field on QA doc) this number of times within last 7 days, user will be kicked. Set it to 0 to disable this feature")

    def __str__(self):
        return f"{self.id} [{self.guild_id}] {self.name} ({self.slug})"