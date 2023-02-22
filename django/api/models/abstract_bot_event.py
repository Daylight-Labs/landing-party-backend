from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from django.apps import apps
from api.model_managers.abstract_bot_event_manager import AbstractBotEventManager

EVENT_TYPE_GUIDED_FLOW = 'EVENT_TYPE_GUIDED_FLOW'
EVENT_TYPE_GUIDED_FLOW_STEP_BUTTON = 'EVENT_TYPE_GUIDED_FLOW_STEP_BUTTON'
EVENT_TYPE_PERMANENT_EMBED_BUTTON = 'EVENT_TYPE_PERMANENT_EMBED_BUTTON'
EVENT_TYPE_SELECT_MENU_OPTION = 'EVENT_TYPE_SELECT_MENU_OPTION'

class AbstractBotEvent(models.Model):
    event_id = models.BigAutoField(primary_key=True)
    triggered_handlers = models.ManyToManyField("AbstractBotEventHandler", related_name="triggered_by", blank=True)
    handler_callbacks = models.ManyToManyField("AbstractBotEventHandler", related_name="callback_set_by", blank=True)

    objects = AbstractBotEventManager()

    def as_leaf_class(self):
        if hasattr(self, 'guidedflow'):
            return self.guidedflow
        if hasattr(self, 'guidedflowstepbutton'):
            return self.guidedflowstepbutton
        if hasattr(self, 'permanentembedbutton'):
            return self.permanentembedbutton
        if hasattr(self, 'showticketmodal'):
            return self.showticketmodal
        if hasattr(self, 'showcustommodal'):
            return self.showcustommodal
        if hasattr(self, 'showselectmenu'):
            return self.showselectmenu
        if hasattr(self, 'showselectmenuoption'):
            return self.showselectmenuoption
        if hasattr(self, 'showcaptcha'):
            return(self.showcaptcha)
        return self

    def __str__(self):
        leaf = self.as_leaf_class()
        if leaf == self:
            return f"Abstract Event #{self.event_id}"
        res = leaf.__str__()
        return res[:100]

    def is_entry_point(self):
        GuidedFlow = apps.get_model('api', 'GuidedFlow')
        GuidedFlowStepButton = apps.get_model('api', 'GuidedFlowStepButton')

        event = self.as_leaf_class()
        if type(event) == GuidedFlow:
            return True
        if type(event) == GuidedFlowStepButton:
            return False
        return False

    def is_enabled(self):
        GuidedFlow = apps.get_model('api', 'GuidedFlow')
        GuidedFlowStepButton = apps.get_model('api', 'GuidedFlowStepButton')

        event = self.as_leaf_class()
        if type(event) == GuidedFlow:
            return event.is_enabled and event.community is not None
        if type(event) == GuidedFlowStepButton:
            return True
        return True

    def to_json(self, with_triggered_handlers):
        GuidedFlow = apps.get_model('api', 'GuidedFlow')
        GuidedFlowStepButton = apps.get_model('api', 'GuidedFlowStepButton')
        PermanentEmbedButton = apps.get_model('api', 'PermanentEmbedButton')
        ShowTicketModal = apps.get_model('api', 'ShowTicketModal')
        ShowCustomModal = apps.get_model('api', 'ShowCustomModal')
        ShowSelectMenu = apps.get_model('api', 'ShowSelectMenu')
        SelectMenuOption = apps.get_model('api', 'SelectMenuOption')
        ShowCaptcha = apps.get_model('api', 'ShowCaptcha')

        event = self.as_leaf_class()

        triggered_handlers = self.triggered_handlers.all()
        handler_callbacks = self.handler_callbacks.all()

        response = {}
        if type(event) == GuidedFlow:
            response = event.serialize_to_json()
        if type(event) == GuidedFlowStepButton:
            response = {
                'event_type': EVENT_TYPE_GUIDED_FLOW_STEP_BUTTON
            }
        if type(event) == PermanentEmbedButton:
            response = {
                'event_type': EVENT_TYPE_PERMANENT_EMBED_BUTTON,
                'button_label': event.button_label,
                'button_style': event.button_style,
                'button_row': event.button_row
            }
        if type(event) == ShowTicketModal:
            response = event.abstractboteventhandler_ptr.to_json()
        if type(event) == ShowCustomModal:
            response = event.abstractboteventhandler_ptr.to_json()
        if type(event) == ShowSelectMenu:
            response = event.abstractboteventhandler_ptr.to_json()
        if type(event) == SelectMenuOption:
            response = {
                'id': str(event.id),
                'label': event.label,
                'description': event.description,
                'event_type': EVENT_TYPE_SELECT_MENU_OPTION,
                'triggered_handlers_ids':
                    list(map(lambda x: x.event_handler_id, event.triggered_handlers.all()))
            }
        if type(event) == ShowCaptcha:
            response = event.abstractboteventhandler_ptr.to_json()

        response['event_id'] = str(self.event_id)

        if with_triggered_handlers:
            response['triggered_handlers'] = list(map(lambda x: x.to_json(), triggered_handlers))
            response['handler_callbacks'] = list(map(lambda x: x.to_json(), handler_callbacks))

        return response

    class Meta:
        ordering = ["event_id"]