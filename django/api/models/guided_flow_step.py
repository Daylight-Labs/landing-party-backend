from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from django.apps import apps
from django.core.files.base import ContentFile
from api.models import GuidedFlow, User
from api.models.abstract_bot_event_handler import AbstractBotEventHandler, EVENT_HANDLER_TYPE_GUIDED_FLOW_STEP, \
    EVENT_HANDLER_TYPE_DELETE_CURRENT_THREAD, EVENT_HANDLER_TYPE_ARCHIVE_CURRENT_THREAD, \
    EVENT_HANDLER_TYPE_SHOW_TICKET_MODAL, EVENT_HANDLER_TYPE_SHOW_CUSTOM_MODAL, \
    EVENT_HANDLER_TYPE_INVITE_USERS_TO_CURRENT_THREAD, \
    EVENT_HANDLER_TYPE_INVITE_USERS_WITH_ROLE_TO_CURRENT_THREAD, \
    EVENT_HANDLER_TYPE_SHOW_SELECT_MENU, EVENT_HANDLER_TYPE_TRIGGER_CALLBACK, \
    EVENT_HANDLER_TYPE_SHOW_CAPTCHA, EVENT_HANDLER_TYPE_GRANT_ROLE
from api.models.abstract_bot_event import AbstractBotEvent
from api.model_managers.deleted_objects_manager import ExcludeDeletedObjectsModelManager

from django.core.validators import MaxValueValidator, MinValueValidator
import requests

class GuidedFlowStep(AbstractBotEventHandler, TimeStampedDeletableModel):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')

    guided_flow = models.ForeignKey(GuidedFlow, on_delete=models.CASCADE, related_name="guided_flow_steps",
                                    null=True, blank=True)
    step_text = models.TextField(null=False, blank=False, max_length=1990)
    help_text = models.TextField(null=True, blank=True, max_length=1990)
    granted_role_id = models.BigIntegerField(null=True, blank=True, default=None)
    granted_role_needs_approval_by = models.ManyToManyField(User,
                                                            related_name="managed_guided_flow_steps_role_approvals",
                                                            blank=True,
                                                            null=True
                                                            )

    file_upload_triggered_handlers = models.ManyToManyField("AbstractBotEventHandler",
                                                            related_name="triggered_by_file_upload",
                                                            blank=True)

    supported_files_formats_csv = models.TextField(null=True, blank=True,
                                                   help_text="Comma separated file formats, e.g. 'png,jpg,gif'. " + \
                                                             "Leave blank to support all file formats")

    def __str__(self):
        return f"Flow step #{self.id} - {self.step_text}"

    def copy(self, new_flow):
        step = GuidedFlowStep.objects.create(
            guided_flow=new_flow,
            step_text=self.step_text,
            help_text=self.help_text,
            granted_role_id=self.granted_role_id,
            supported_files_formats_csv=self.supported_files_formats_csv
        )
        for u in self.granted_role_needs_approval_by.all():
            step.granted_role_needs_approval_by.add(u)
        return step

    def serialize_to_json(self, triggered_handlers_as_ids=False):
        event_handler = self
        resp = {
            'handler_type': EVENT_HANDLER_TYPE_GUIDED_FLOW_STEP,
            'step_text': event_handler.step_text,
            'help_text': event_handler.help_text,
            'granted_role_id': event_handler.granted_role_id,
            'granted_role_needs_approval_by': list(
                map(lambda x: x.discord_user_id, event_handler.granted_role_needs_approval_by.all())),
            'flow_event_id': event_handler.guided_flow.event_id,
            'guided_flow_step_id': event_handler.id,
            'attached_files': list(map(lambda x: {
                'name': x.name,
                'file': x.file.name
            }, event_handler.attached_files.all())),
            'buttons': list(map(lambda x: {
                'button_label': x.button_label,
                'button_style': x.button_style,
                'event_id': str(x.event_id),
                'triggered_handlers_ids':  list(map(lambda x: x.event_handler_id, x.triggered_handlers.all())),
                'button_row': x.button_row
            }, event_handler.step_buttons.filter(deleted_on__isnull=True).all())),
            'supported_files_formats_csv': event_handler.supported_files_formats_csv,
            'event_handler_id': self.event_handler_id
        }
        if triggered_handlers_as_ids:
            resp['file_upload_triggered_handlers_ids'] = list(
                map(lambda x: x.event_handler_id, event_handler.file_upload_triggered_handlers.all()))
        else:
            resp['file_upload_triggered_handlers'] = list(
                map(lambda x: x.to_json(), event_handler.file_upload_triggered_handlers.all()))

        return resp

    @staticmethod
    def create_from_json(data, new_flow):
        GuidedFlowStepButton = apps.get_model('api', 'GuidedFlowStepButton')
        GuidedFlowStepAttachedFile = apps.get_model('api', 'GuidedFlowStepAttachedFile')

        step = GuidedFlowStep.objects.create(
            guided_flow=new_flow,
            step_text=data['step_text'],
            help_text=data['help_text'],
            granted_role_id=data['granted_role_id'],
            supported_files_formats_csv=data['supported_files_formats_csv']
        )
        for u_id in data['granted_role_needs_approval_by']:
            if u_id is None:
                continue
            u = User.objects.filter(discord_user_id=u_id).first()
            if u is not None:
                step.granted_role_needs_approval_by.add(u)

        buttons_res = []

        for button_data in data['buttons']:
            button = GuidedFlowStepButton.objects.create(
                flow_step=step,
                button_label=button_data['button_label'],
                button_style=button_data['button_style']
            )
            buttons_res.append({
                "original_json": button_data,
                "created_object": button
            })

        for attached_file in data['attached_files']:
            name = attached_file['name']
            file = attached_file['file']

            obj = GuidedFlowStepAttachedFile.objects.create(
                name=name,
                step=step
            )

            url = f'https://bn-bot-storage.s3.amazonaws.com/{file}'

            response = requests.get(url)

            obj.file.save(file, ContentFile(response.content), save=True)

        return [step, buttons_res]

class GrantRole(AbstractBotEventHandler):
    granted_role_id = models.BigIntegerField(null=True, blank=True, default=None)
    granted_role_needs_approval_by = models.ManyToManyField(User,
                                                            related_name="managed_granted_roles",
                                                            blank=True,
                                                            null=True
                                                            )
    label = models.TextField(null=True, blank=True,
                             help_text="Not used by bot. Used only as a label in admin panel")

    def __str__(self):
        usernames = ', '.join(map(lambda x: x.discord_username if x.discord_username else str(x.discord_user_id),
                                  self.granted_role_needs_approval_by.all()))
        return f"Grant role: {self.granted_role_id} ({self.label}) " + (f"with approval by {usernames}" if len(self.granted_role_needs_approval_by.all()) else "without approval")

    def copy(self):
        copy = GrantRole.objects.create()
        for u in self.granted_role_needs_approval_by.all():
            copy.granted_role_needs_approval_by.add(u)
        copy.granted_role_id = self.granted_role_id
        return copy

    def serialize_to_json(self):
        event_handler = self
        return {
            'handler_type': EVENT_HANDLER_TYPE_GRANT_ROLE,
            'event_handler_id': self.event_handler_id,
            'granted_role_needs_approval_by': list(map(lambda x: x.discord_user_id, event_handler.granted_role_needs_approval_by.all())),
            'granted_role_id': self.granted_role_id
        }

    @staticmethod
    def create_from_json(data, new_flow):
        copy = GrantRole.objects.create()
        for u_id in data['granted_role_needs_approval_by']:
            if u_id is None:
                continue
            u = User.objects.filter(discord_user_id=u_id).first()
            if u is not None:
                copy.granted_role_needs_approval_by.add(u)
        copy.granted_role_id = data['granted_role_id']
        return copy

class DeleteCurrentThread(AbstractBotEventHandler):
    def __str__(self):
        return "Delete Current Thread/Channel"

    def serialize_to_json(self):
        return {
            'event_handler_id': self.event_handler_id,
            'handler_type': EVENT_HANDLER_TYPE_DELETE_CURRENT_THREAD
        }

class ArchiveCurrentThread(AbstractBotEventHandler):
    def __str__(self):
        return "Archive Current Thread/Delete Channel"

    def serialize_to_json(self):
        return {
            'event_handler_id': self.event_handler_id,
            'handler_type': EVENT_HANDLER_TYPE_ARCHIVE_CURRENT_THREAD
        }

class ShowTicketModal(AbstractBotEventHandler, AbstractBotEvent):
    objects = models.Manager()

    label = models.TextField(null=True, blank=True,
                             help_text="Not used by bot. Used only as a label in admin panel")

    modal_title = models.TextField(null=False, default="Create a Ticket", max_length=45)

    subject_label = models.TextField(null=False, default="Subject", max_length=45)
    subject_placeholder = models.TextField(null=False, default="Subject", max_length=100)

    describe_label = models.TextField(null=False, default="Please describe your issue", max_length=45)
    describe_placeholder = models.TextField(null=False, default="Please describe your issue", max_length=100)

    def __str__(self):
        triggered_handlers = self.triggered_handlers.all()
        if len(triggered_handlers) == 0:
            s = 'nothing'
        else:
            s = '; '.join(map(str, triggered_handlers))
        return f"#{self.event_id} Show Ticket Modal ({self.label or ''}) and then go to {s}"

    def copy(self, new_flow):
        copy = ShowTicketModal.objects.create(
            subject_label=self.subject_label,
            subject_placeholder=self.subject_placeholder,
            describe_label=self.describe_label,
            describe_placeholder=self.describe_placeholder,
            modal_title=self.modal_title
        )
        return copy

    def serialize_to_json(self, triggered_handlers_as_ids=False):
        resp = {
            'handler_type': EVENT_HANDLER_TYPE_SHOW_TICKET_MODAL,
            'event_type': EVENT_HANDLER_TYPE_SHOW_TICKET_MODAL,
            'event_id': self.event_id,
            'event_handler_id': self.event_handler_id,
            'subject_label': self.subject_label,
            'subject_placeholder': self.subject_placeholder,
            'describe_label': self.describe_label,
            'describe_placeholder': self.describe_placeholder,
            'modal_title': self.modal_title
        }

        if triggered_handlers_as_ids:
            resp['triggered_handlers_ids'] = \
                list(map(lambda x: x.event_handler_id, self.triggered_handlers.all()))

        return resp

    @staticmethod
    def create_from_json(data, new_flow):
        return ShowTicketModal.objects.create(
            subject_label=data['subject_label'],
            subject_placeholder=data['subject_placeholder'],
            describe_label=data['describe_label'],
            describe_placeholder=data['describe_placeholder'],
            modal_title=data['modal_title']
        )

class ShowCaptcha(AbstractBotEventHandler, AbstractBotEvent):

    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')

    class CaptchaType(models.TextChoices):
        MATH = 'MA'
        TEXT = 'TE'
    
    captcha_type = models.CharField(
        max_length= 2,
        choices=CaptchaType.choices,
        default=CaptchaType.MATH,
        null=False
    )

    captcha_message = models.TextField(null=True, blank=True, max_length=1990)

    verify_button_text = models.TextField(null=True, blank=True, max_length=90,
                                          help_text="Default is 'Verify answer'")

    label = models.TextField(null=True, blank=True,
                             help_text="Not used by bot. Used only as a label in admin panel")

    objects = models.Manager()
    
    def __str__(self):
        triggered_handlers = self.triggered_handlers.all()
        if len(triggered_handlers) == 0:
            s = 'nothing'
        else:
            s = '; '.join(map(str, triggered_handlers))
        return f"#{self.event_id} Show Captcha ({self.label or ''}) and then go to {s}"
    
    def copy(self, new_flow):
        copy = ShowCaptcha.objects.create()
        copy.captcha_message = self.captcha_message
        return copy

    def serialize_to_json(self, triggered_handlers_as_ids=False):
        resp = {
            'handler_type': EVENT_HANDLER_TYPE_SHOW_CAPTCHA,
            'event_type': EVENT_HANDLER_TYPE_SHOW_CAPTCHA,
            'event_id': self.event_id,
            'event_handler_id': self.event_handler_id,
            'captcha_message': self.captcha_message,
            'verify_button_text': self.verify_button_text,
            "captcha_type": self.captcha_type
        }

        if triggered_handlers_as_ids:
            resp['triggered_handlers_ids'] = \
                list(map(lambda x: x.event_handler_id, self.triggered_handlers.all()))

        return resp

    @staticmethod
    def create_from_json(data, new_flow):
        return ShowCaptcha.objects.create()

class ShowCustomModal(AbstractBotEventHandler, AbstractBotEvent, TimeStampedDeletableModel):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')

    title = models.TextField(null=False, default="")

    csv_export_is_anonymous = models.BooleanField(null=False, default=False,
                                                  help_text="Affects only export from Django admin")

    label = models.TextField(null=True, blank=True,
                             help_text="Not used by bot. Used only as a label in admin panel")

    google_spreadsheet_id = models.CharField(max_length=100, null=True, blank=True,
                                             help_text="Spreadsheet ID where to export modal submissions (with visible usernames and user ids).\n" + \
                                                       "Make sure bot has edit access to this spreadsheet. \n" + \
                                                       "Spreadsheet ID can be found in spreadsheet URL - https://docs.google.com/spreadsheets/d/{ID}/edit#gid=0.\n" + \
                                                       "Submissions are exported daily")

    anonymized_google_spreadsheet_id = models.CharField(max_length=100, null=True, blank=True,
                                                        help_text="Spreadsheet ID where to export modal submissions (with usernames and user ids anonymized).\n" + \
                                                                  "Make sure bot has edit access to this spreadsheet. \n" + \
                                                                  "Spreadsheet ID can be found in spreadsheet URL - https://docs.google.com/spreadsheets/d/{ID}/edit#gid=0.\n" + \
                                                                  "Submissions are exported daily")

    objects = models.Manager()
    def __str__(self):
        triggered_handlers = self.triggered_handlers.all()
        if len(triggered_handlers) == 0:
            s = 'nothing'
        else:
            s = '; '.join(map(str, triggered_handlers))
        return f"Show Custom Modal ({self.label or ''}) #{self.event_id} ({self.title}) ({self.fields.filter(deleted_on__isnull=True).count()} fields) and then go to {s}"

    def copy(self, new_flow):
        copy = ShowCustomModal.objects.create(
            title=self.title
        )
        for f in self.fields.all():
            f_copy = f.copy(modal=copy)
            copy.fields.add(f_copy)
        return copy

    def serialize_to_json(self, triggered_handlers_as_ids=False):
        event_handler = self
        resp = {
            'handler_type': EVENT_HANDLER_TYPE_SHOW_CUSTOM_MODAL,
            'event_type': EVENT_HANDLER_TYPE_SHOW_CUSTOM_MODAL,
            'event_id': event_handler.event_id,
            'event_handler_id': self.event_handler_id,
            'title': event_handler.title,
            'show_custom_modal_id': event_handler.id,
            'fields': list(map(lambda x: {
                'id': str(x.id),
                'type': x.type,
                'label': x.label,
                'placeholder': x.placeholder,
                'style': x.style,
                'min_length': x.min_length,
                'max_length': x.max_length,
                'required': x.required
            }, event_handler.fields.filter(deleted_on__isnull=True).all()))
        }
        if triggered_handlers_as_ids:
            resp['triggered_handlers_ids'] = \
                list(map(lambda x: x.event_handler_id, self.triggered_handlers.all()))

        return resp

    @staticmethod
    def create_from_json(data, new_flow):
        copy = ShowCustomModal.objects.create(
            title=data['title']
        )
        for f in data['fields']:
            f_copy = CustomModalField.create_from_json(f, modal=copy)
            copy.fields.add(f_copy)
        return copy

MODAL_FIELD_TYPE_TEXT_INPUT = 'TEXT_INPUT'

MODAL_INPUT_STYLE_SHORT = 'SHORT'
MODAL_INPUT_STYLE_LONG = 'LONG'

class CustomModalField(TimeStampedDeletableModel):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')

    type = models.TextField(choices=[
        (MODAL_FIELD_TYPE_TEXT_INPUT, MODAL_FIELD_TYPE_TEXT_INPUT)
    ], null=False, default=MODAL_FIELD_TYPE_TEXT_INPUT)

    modal = models.ForeignKey(ShowCustomModal, on_delete=models.CASCADE, related_name="fields")

    label = models.TextField(null=False, max_length=45)
    placeholder = models.TextField(null=False, default="", max_length=100)
    style = models.TextField(choices=[
        (MODAL_INPUT_STYLE_SHORT, MODAL_INPUT_STYLE_SHORT),
        (MODAL_INPUT_STYLE_LONG, MODAL_INPUT_STYLE_LONG)
    ], null=False, default=MODAL_INPUT_STYLE_LONG)

    min_length = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(3999),
            MinValueValidator(0)
        ],
        null=False
    )
    max_length = models.IntegerField(
        default=3999,
        validators=[
            MaxValueValidator(3999),
            MinValueValidator(1)
        ],
        null=False
    )
    required = models.BooleanField(null=False, default=True)

    def copy(self, modal):
        copy = CustomModalField.objects.create(
            type=self.type,
            modal=modal,
            label=self.label,
            placeholder=self.placeholder,
            style=self.style,
            min_length=self.min_length,
            max_length=self.max_length,
            required=self.required
        )
        return copy

    @staticmethod
    def create_from_json(data, modal):
        copy = CustomModalField.objects.create(
            type=data['type'],
            modal=modal,
            label=data['label'],
            placeholder=data['placeholder'],
            style=data['style'],
            min_length=data['min_length'],
            max_length=data['max_length'],
            required=data['required']
        )
        return copy

class TriggerCallback(AbstractBotEventHandler):
    def __str__(self):
        return "Trigger Callback (Subflows only)"

    def serialize_to_json(self):
        event_handler = self
        return {
            'handler_type': EVENT_HANDLER_TYPE_TRIGGER_CALLBACK,
            'event_handler_id': self.event_handler_id
        }

class InviteUsersToCurrentThread(AbstractBotEventHandler):
    users_to_invite = models.ManyToManyField(User,
                                             related_name="users_to_be",
                                             blank=False
                                             )
    def __str__(self):
        usernames = ', '.join(map(lambda x: x.discord_username if x.discord_username else str(x.discord_user_id),
                                  self.users_to_invite.all()))
        return f"Invite users: {usernames}"

    def copy(self):
        copy = InviteUsersToCurrentThread.objects.create()
        for u in self.users_to_invite.all():
            copy.users_to_invite.add(u)
        return copy

    def serialize_to_json(self):
        event_handler = self
        return {
            'handler_type': EVENT_HANDLER_TYPE_INVITE_USERS_TO_CURRENT_THREAD,
            'event_handler_id': self.event_handler_id,
            'users_ids_to_invite': list(map(lambda x: x.discord_user_id, event_handler.users_to_invite.all()))
        }

    @staticmethod
    def create_from_json(data, new_flow):
        copy = InviteUsersToCurrentThread.objects.create()
        for u_id in data['users_ids_to_invite']:
            if u_id is None:
                continue
            u = User.objects.filter(discord_user_id=u_id).first()
            if u is not None:
                copy.users_to_invite.add(u)
        return copy

class InviteUsersWithRoleToCurrentThread(AbstractBotEventHandler):
    role_id = models.BigIntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return f"Invite users with role {self.role_id}"

    def copy(self):
        copy = InviteUsersWithRoleToCurrentThread.objects.create(
            role_id=self.role_id
        )
        return copy

    def serialize_to_json(self):
        event_handler = self
        return {
            'handler_type': EVENT_HANDLER_TYPE_INVITE_USERS_WITH_ROLE_TO_CURRENT_THREAD,
            'event_handler_id': self.event_handler_id,
            'role_id': event_handler.role_id
        }

    @staticmethod
    def create_from_json(data, flow):
        copy = InviteUsersWithRoleToCurrentThread.objects.create(
            role_id=data['role_id']
        )
        return copy

class ShowSelectMenu(AbstractBotEventHandler, AbstractBotEvent, TimeStampedDeletableModel):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')

    message_text = models.TextField(null=False, default="")

    placeholder = models.TextField(null=False, default="", max_length=150)

    csv_export_is_anonymous = models.BooleanField(null=False, default=False,
                                                  help_text="Affects only export from Django admin")

    label = models.TextField(null=True, blank=True,
                             help_text="Not used by bot. Used only as a label in admin panel")

    min_values = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(25),
            MinValueValidator(1)
        ],
        null=False
    )
    max_values = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(25),
            MinValueValidator(1)
        ],
        null=False
    )

    google_spreadsheet_id = models.CharField(max_length=100, null=True, blank=True,
                                             help_text="Spreadsheet ID where to export menu submissions (with visible usernames and user ids).\n" + \
                                                       "Make sure bot has edit access to this spreadsheet. \n" + \
                                                       "Spreadsheet ID can be found in spreadsheet URL - https://docs.google.com/spreadsheets/d/{ID}/edit#gid=0.\n" + \
                                                       "Submissions are exported daily")

    anonymized_google_spreadsheet_id = models.CharField(max_length=100, null=True, blank=True,
                                                        help_text="Spreadsheet ID where to export menu submissions (with usernames and user ids anonymized).\n" + \
                                                                  "Make sure bot has edit access to this spreadsheet. \n" + \
                                                                  "Spreadsheet ID can be found in spreadsheet URL - https://docs.google.com/spreadsheets/d/{ID}/edit#gid=0.\n" + \
                                                                  "Submissions are exported daily")

    objects = models.Manager()

    def __str__(self):
        triggered_handlers = self.triggered_handlers.all()
        if len(triggered_handlers) == 0:
            s = 'nothing'
        else:
            s = '; '.join(map(str, triggered_handlers))
        return f"Show SelectMenu ({self.label or ''}) #{self.event_id} ({self.message_text}) ({self.options.filter(deleted_on__isnull=True).count()} options) and then go to {s}"

    def copy(self, new_flow):
        copy = ShowSelectMenu.objects.create(
            message_text=self.message_text,
            placeholder=self.placeholder,
            min_values=self.min_values,
            max_values=self.max_values,
        )
        return copy

    def serialize_to_json(self, triggered_handlers_as_ids=False):
        event_handler = self
        resp = {
            'handler_type': EVENT_HANDLER_TYPE_SHOW_SELECT_MENU,
            'event_type': EVENT_HANDLER_TYPE_SHOW_SELECT_MENU,
            'event_id': event_handler.event_id,
            'event_handler_id': self.event_handler_id,
            'message_text': event_handler.message_text,
            'placeholder': event_handler.placeholder,
            'min_values': event_handler.min_values,
            'max_values': event_handler.max_values,
            'show_select_menu_id': event_handler.id,
            'options': list(map(lambda x: x.to_json(with_triggered_handlers=False),
                                event_handler.options.filter(deleted_on__isnull=True).order_by('order').all()))
        }
        if triggered_handlers_as_ids:
            resp['triggered_handlers_ids'] = \
                list(map(lambda x: x.event_handler_id, self.triggered_handlers.all()))
        return resp

    @staticmethod
    def create_from_json(data, flow):
        copy = ShowSelectMenu.objects.create(
            message_text=data['message_text'],
            placeholder=data['placeholder'],
            min_values=data['min_values'],
            max_values=data['max_values']
        )

        options_res = []

        for o in data['options']:
            option = SelectMenuOption.create_from_json(o, menu=copy)
            options_res.append({
                "original_json": o,
                "created_object": option
            })
        return [copy, options_res]

class SelectMenuOption(AbstractBotEvent, TimeStampedDeletableModel):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')

    menu = models.ForeignKey(ShowSelectMenu, on_delete=models.CASCADE, related_name="options")

    label = models.TextField(null=False, max_length=100)
    description = models.TextField(null=False, default="", blank=True, max_length=100)

    order = models.FloatField(null=True)

    objects = ExcludeDeletedObjectsModelManager()

    def copy(self, menu):
        option = SelectMenuOption.objects.create(
            menu=menu,
            label=self.label,
            description=self.description,
            order=self.order
        )
        return option

    @staticmethod
    def create_from_json(data, menu):
        option = SelectMenuOption.objects.create(
            menu=menu,
            label=data['label'],
            description=data['description'],
            order=data.get('order')
        )
        return option