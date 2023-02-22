from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from api.models import User, Community
from api.models.abstract_bot_event import AbstractBotEvent, EVENT_TYPE_GUIDED_FLOW
from api.models.abstract_bot_event_handler import AbstractBotEventHandler


class GuidedFlow(AbstractBotEvent, AbstractBotEventHandler, TimeStampedDeletableModel):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')

    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="guided_flows",
                                  blank=True, null=True)
    moderators_to_contact = models.ManyToManyField(User, related_name="moderated_guided_flows", blank=True)

    slash_command_name = models.CharField(max_length=50, null=True, blank=True)

    flow_label = models.CharField(max_length=50, null=False, blank=False, default="onboarding")

    channel_name = models.CharField(max_length=50, null=False, blank=False, default="onboarding")

    is_ephemeral = models.BooleanField(null=False, default=False,
                                       help_text="If not checked, channels/threads are used (depending on guild boost lvl)")

    is_enabled = models.BooleanField(null=False, default=True)

    google_spreadsheet_id = models.CharField(max_length=100, null=True, blank=True,
                                             help_text="Spreadsheet ID where to export menu/modal submissions (with visible usernames and user ids).\n" + \
                                                       "Make sure bot has edit access to this spreadsheet. \n" + \
                                                       "Spreadsheet ID can be found in spreadsheet URL - https://docs.google.com/spreadsheets/d/{ID}/edit#gid=0.\n" + \
                                                       "Submissions are exported daily")

    anonymized_google_spreadsheet_id = models.CharField(max_length=100, null=True, blank=True,
                                                        help_text="Spreadsheet ID where to export menu/modal submissions (with usernames and user ids anonymized).\n" + \
                                                        "Make sure bot has edit access to this spreadsheet. \n" + \
                                                        "Spreadsheet ID can be found in spreadsheet URL - https://docs.google.com/spreadsheets/d/{ID}/edit#gid=0.\n" + \
                                                        "Submissions are exported daily")

    auto_archive_duration = models.IntegerField(null=False, default=1440, choices=[
        (60, 60),
        (1440, 1440),
        (4320, 4320),
        (10080, 10080)
    ] )

    objects = models.Manager()

    def __str__(self):
        enabled_label = "Enabled" if self.is_enabled else "Disabled"
        return f"Guided Flow #{self.id} - {self.slash_command_name} - {self.community} - {enabled_label}"

    class Meta:
        unique_together = (('community', 'slash_command_name',), ('community', 'flow_label',), ('community', 'channel_name',))

    def copy(self):
        copy = GuidedFlow.objects.create(
            community=self.community,
            slash_command_name=self.slash_command_name + '-copy',
            flow_label=self.flow_label + '-copy',
            channel_name=self.channel_name + '-copy',
            is_enabled=self.is_enabled,
            auto_archive_duration=self.auto_archive_duration
        )

        for u in self.moderators_to_contact.all():
            copy.moderators_to_contact.add(u)

        return copy

    def serialize_to_json(self, triggered_handlers_as_ids=False):
        event = self
        resp = {
            'event_type': EVENT_TYPE_GUIDED_FLOW,
            'handler_type': EVENT_TYPE_GUIDED_FLOW,
            'guild_ids': [str(event.community.guild_id)] if event.community is not None else [],
            'moderators_to_contact': list(map(lambda u: str(u.discord_user_id), event.moderators_to_contact.all())),
            'slash_command_name': event.slash_command_name,
            'flow_id': event.id,
            'flow_label': event.flow_label,
            'channel_name': event.channel_name,
            'auto_archive_duration': event.auto_archive_duration,
            'event_handler_id': self.event_handler_id,
            'is_ephemeral': event.is_ephemeral
        }
        if triggered_handlers_as_ids:
            resp['triggered_handlers_ids'] = list(map(lambda x: x.event_handler_id, self.triggered_handlers.all()))
        return resp

    @staticmethod
    def create_from_json(data):
        copy = GuidedFlow.objects.create(
            slash_command_name=data['slash_command_name'],
            flow_label=data['flow_label'],
            channel_name=data['channel_name'],
            is_enabled=True,
            is_ephemeral=data['is_ephemeral'],
            auto_archive_duration=data['auto_archive_duration']
        )

        for u_id in data['moderators_to_contact']:
            if u_id is None:
                continue
            u = User.objects.filter(discord_user_id=u_id).first()
            if u is not None:
                copy.moderators_to_contact.add(u)

        return copy