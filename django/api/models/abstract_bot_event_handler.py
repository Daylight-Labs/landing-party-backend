from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from django.apps import apps
from .abstract_bot_event import EVENT_TYPE_GUIDED_FLOW

EVENT_HANDLER_TYPE_GUIDED_FLOW = EVENT_TYPE_GUIDED_FLOW
EVENT_HANDLER_TYPE_GUIDED_FLOW_STEP = 'EVENT_HANDLER_TYPE_GUIDED_FLOW_STEP'
EVENT_HANDLER_TYPE_GRANT_ROLE = 'EVENT_HANDLER_TYPE_GRANT_ROLE'
EVENT_HANDLER_TYPE_DELETE_CURRENT_THREAD = 'EVENT_HANDLER_TYPE_DELETE_CURRENT_THREAD'
EVENT_HANDLER_TYPE_ARCHIVE_CURRENT_THREAD = 'EVENT_HANDLER_TYPE_ARCHIVE_CURRENT_THREAD'
EVENT_HANDLER_TYPE_INVITE_USERS_TO_CURRENT_THREAD = 'EVENT_HANDLER_TYPE_INVITE_USERS_TO_CURRENT_THREAD'
EVENT_HANDLER_TYPE_SHOW_TICKET_MODAL = 'EVENT_HANDLER_TYPE_SHOW_TICKET_MODAL'
EVENT_HANDLER_TYPE_SHOW_CUSTOM_MODAL = 'EVENT_HANDLER_TYPE_SHOW_CUSTOM_MODAL'
EVENT_HANDLER_TYPE_SHOW_SELECT_MENU = 'EVENT_HANDLER_TYPE_SHOW_SELECT_MENU'
EVENT_HANDLER_TYPE_TRIGGER_CALLBACK = 'EVENT_HANDLER_TYPE_TRIGGER_CALLBACK'
EVENT_HANDLER_TYPE_INVITE_USERS_WITH_ROLE_TO_CURRENT_THREAD = \
    'EVENT_HANDLER_TYPE_INVITE_USERS_WITH_ROLE_TO_CURRENT_THREAD'
EVENT_HANDLER_TYPE_SHOW_CAPTCHA = 'EVENT_HANDLER_TYPE_SHOW_CAPTCHA'

class AbstractBotEventHandler(models.Model):
    event_handler_id = models.BigAutoField(primary_key=True)

    def as_leaf_class(self):
        if hasattr(self, 'deletecurrentthread'):
            return self.deletecurrentthread
        if hasattr(self, 'archivecurrentthread'):
            return self.archivecurrentthread
        if hasattr(self, 'guidedflowstep'):
            return self.guidedflowstep
        if hasattr(self, 'inviteuserstocurrentthread'):
            return self.inviteuserstocurrentthread
        if hasattr(self, 'inviteuserswithroletocurrentthread'):
            return self.inviteuserswithroletocurrentthread
        if hasattr(self, 'showticketmodal'):
            return self.showticketmodal
        if hasattr(self, 'showcustommodal'):
            return self.showcustommodal
        if hasattr(self, 'showselectmenu'):
            return self.showselectmenu
        if hasattr(self, 'guidedflow'):
            return self.guidedflow
        if hasattr(self, 'triggercallback'):
            return self.triggercallback
        if hasattr(self, 'showcaptcha'):
            return(self.showcaptcha)
        if hasattr(self, 'grantrole'):
            return self.grantrole
        return self

    def __str__(self):
        leaf = self.as_leaf_class()
        if leaf == self:
            return f"Abstract Event Handler #{self.event_handler_id}"
        res = leaf.__str__()
        return res[:100]

    def create_copy_recursive(self, original_flow, new_flow=None, event_handler_copied_cache=None,
                              serialize_to_array_not_db=None, crash_in_case_of_subflow=True):

        write_to_db = serialize_to_array_not_db is None

        DeleteCurrentThread = apps.get_model('api', 'DeleteCurrentThread')
        GuidedFlow = apps.get_model('api', 'GuidedFlow')
        GuidedFlowStep = apps.get_model('api', 'GuidedFlowStep')
        GrantRole = apps.get_model('api', 'GrantRole')
        ArchiveCurrentThread = apps.get_model('api', 'ArchiveCurrentThread')
        InviteUsersToCurrentThread = apps.get_model('api', 'InviteUsersToCurrentThread')
        ShowTicketModal = apps.get_model('api', 'ShowTicketModal')
        ShowCaptcha = apps.get_model('api', 'ShowCaptcha')
        ShowCustomModal = apps.get_model('api', 'ShowCustomModal')
        ShowSelectMenu = apps.get_model('api', 'ShowSelectMenu')
        TriggerCallback = apps.get_model('api', 'TriggerCallback')
        InviteUsersWithRoleToCurrentThread = apps.get_model('api', 'InviteUsersWithRoleToCurrentThread')

        event_handler = self.as_leaf_class()

        if event_handler_copied_cache is None:
            event_handler_copied_cache = {}

        # This is needed in order to prevent infinite loop for recursive steps,
        # And duplicating same event handlers multiple times
        if self.event_handler_id in event_handler_copied_cache:
            return event_handler_copied_cache[self.event_handler_id]

        if type(event_handler) == GuidedFlow:
            if (new_flow is None) or (not crash_in_case_of_subflow):
                if serialize_to_array_not_db is not None:
                    copy = event_handler.serialize_to_json(triggered_handlers_as_ids=True)
                    serialize_to_array_not_db.append(copy)
                else:
                    copy = event_handler.copy()
                event_handler_copied_cache[event_handler.event_handler_id] = copy
                for h in event_handler.triggered_handlers.all():
                    h_copy = h.create_copy_recursive(original_flow, new_flow=copy,
                                                     event_handler_copied_cache=event_handler_copied_cache,
                                                     serialize_to_array_not_db=serialize_to_array_not_db,
                                                     crash_in_case_of_subflow=crash_in_case_of_subflow)
                    if write_to_db:
                        copy.triggered_handlers.add(h_copy)
                return copy
            else:
                raise Exception("Copying nested flows does not work yet")

        if new_flow is None:
            raise Exception("Guided flow should be the very first event handler copied")

        if type(event_handler) == TriggerCallback:
            if serialize_to_array_not_db is not None:
                copy = event_handler.serialize_to_json()
                serialize_to_array_not_db.append(copy)
            else:
                copy = event_handler
            return copy
        if type(event_handler) == GrantRole:
            if serialize_to_array_not_db is not None:
                copy = event_handler.serialize_to_json()
                serialize_to_array_not_db.append(copy)
            else:
                copy = event_handler.copy()
            return copy
        if type(event_handler) == GuidedFlowStep:
            if serialize_to_array_not_db is not None:
                copy = event_handler.serialize_to_json(triggered_handlers_as_ids=True)
                serialize_to_array_not_db.append(copy)
            else:
                copy = event_handler.copy(new_flow)
            event_handler_copied_cache[event_handler.event_handler_id] = copy
            for b in event_handler.step_buttons.all():
                if write_to_db:
                    b_copy = b.copy(flow_step=copy)
                for h in b.triggered_handlers.all():
                    h_copy = h.create_copy_recursive(original_flow, new_flow,
                                                     event_handler_copied_cache=event_handler_copied_cache,
                                                     serialize_to_array_not_db=serialize_to_array_not_db,
                                                     crash_in_case_of_subflow=crash_in_case_of_subflow)
                    if write_to_db:
                        b_copy.triggered_handlers.add(h_copy)
            for h in event_handler.file_upload_triggered_handlers.all():
                h_copy = h.create_copy_recursive(original_flow, new_flow,
                                                 event_handler_copied_cache=event_handler_copied_cache,
                                                 serialize_to_array_not_db=serialize_to_array_not_db,
                                                 crash_in_case_of_subflow=crash_in_case_of_subflow)
                if write_to_db:
                    copy.file_upload_triggered_handlers.add(h_copy)
            if write_to_db:
                for f in event_handler.attached_files.all():
                    f.copy(step=copy)
            return copy
        if type(event_handler) == DeleteCurrentThread:
            if serialize_to_array_not_db is not None:
                copy = event_handler.serialize_to_json()
                serialize_to_array_not_db.append(copy)
            else:
                copy = event_handler
            return copy
        if type(event_handler) == ArchiveCurrentThread:
            if serialize_to_array_not_db is not None:
                copy = event_handler.serialize_to_json()
                serialize_to_array_not_db.append(copy)
            else:
                copy = event_handler
            return copy
        if type(event_handler) == ShowTicketModal:
            if serialize_to_array_not_db is not None:
                copy = event_handler.serialize_to_json(triggered_handlers_as_ids=True)
                serialize_to_array_not_db.append(copy)
            else:
                copy = event_handler.copy(new_flow)
            event_handler_copied_cache[event_handler.event_handler_id] = copy

            for h in event_handler.triggered_handlers.all():
                h_copy = h.create_copy_recursive(original_flow, new_flow,
                                                 event_handler_copied_cache=event_handler_copied_cache,
                                                 serialize_to_array_not_db=serialize_to_array_not_db,
                                                 crash_in_case_of_subflow=crash_in_case_of_subflow)
                if write_to_db:
                    copy.triggered_handlers.add(h_copy)
            return copy
        if type(event_handler) == ShowCaptcha:
            if serialize_to_array_not_db is not None:
                copy = event_handler.serialize_to_json()
                serialize_to_array_not_db.append(copy)
            else:
                copy = event_handler.copy(new_flow)
            event_handler_copied_cache[event_handler.event_handler_id] = copy
            for h in event_handler.triggered_handlers.all():
                h_copy = h.create_copy_recursive(original_flow, new_flow,
                                                 event_handler_copied_cache=event_handler_copied_cache,
                                                 serialize_to_array_not_db=serialize_to_array_not_db,
                                                 crash_in_case_of_subflow=crash_in_case_of_subflow)
                if write_to_db:
                    copy.triggered_handlers.add(h_copy)
            return copy
        if type(event_handler) == ShowCustomModal:
            if serialize_to_array_not_db is not None:
                copy = event_handler.serialize_to_json(triggered_handlers_as_ids=True)
                serialize_to_array_not_db.append(copy)
            else:
                copy = event_handler.copy(new_flow)
            event_handler_copied_cache[event_handler.event_handler_id] = copy
            for h in event_handler.triggered_handlers.all():
                h_copy = h.create_copy_recursive(original_flow, new_flow,
                                                 event_handler_copied_cache=event_handler_copied_cache,
                                                 serialize_to_array_not_db=serialize_to_array_not_db,
                                                 crash_in_case_of_subflow=crash_in_case_of_subflow)
                if write_to_db:
                    copy.triggered_handlers.add(h_copy)
            return copy
        if type(event_handler) == ShowSelectMenu:
            if serialize_to_array_not_db is not None:
                copy = event_handler.serialize_to_json(triggered_handlers_as_ids=True)
                serialize_to_array_not_db.append(copy)
            else:
                copy = event_handler.copy(new_flow)

            event_handler_copied_cache[event_handler.event_handler_id] = copy
            for h in event_handler.triggered_handlers.all():
                h_copy = h.create_copy_recursive(original_flow, new_flow,
                                                 event_handler_copied_cache=event_handler_copied_cache,
                                                 serialize_to_array_not_db=serialize_to_array_not_db,
                                                 crash_in_case_of_subflow=crash_in_case_of_subflow)
                if write_to_db:
                    copy.triggered_handlers.add(h_copy)

            for o in event_handler.options.all():
                if write_to_db:
                    o_copy = o.copy(menu=copy)
                    copy.options.add(o_copy)
                for h in o.triggered_handlers.all():
                    h_copy = h.create_copy_recursive(original_flow, new_flow,
                                                     event_handler_copied_cache=event_handler_copied_cache,
                                                     serialize_to_array_not_db=serialize_to_array_not_db,
                                                     crash_in_case_of_subflow=crash_in_case_of_subflow)
                    if write_to_db:
                        o_copy.triggered_handlers.add(h_copy)
            return copy
        if type(event_handler) == InviteUsersToCurrentThread:
            if serialize_to_array_not_db is not None:
                copy = event_handler.serialize_to_json()
                serialize_to_array_not_db.append(copy)
            else:
                copy = event_handler.copy()
            return copy
        if type(event_handler) == InviteUsersWithRoleToCurrentThread:
            if serialize_to_array_not_db is not None:
                copy = event_handler.serialize_to_json()
                serialize_to_array_not_db.append(copy)
            else:
                copy = event_handler.copy()
            return copy

    @staticmethod
    def from_json(data, flow):
        DeleteCurrentThread = apps.get_model('api', 'DeleteCurrentThread')
        GuidedFlow = apps.get_model('api', 'GuidedFlow')
        GuidedFlowStep = apps.get_model('api', 'GuidedFlowStep')
        GrantRole = apps.get_model('api', 'GrantRole')
        ArchiveCurrentThread = apps.get_model('api', 'ArchiveCurrentThread')
        InviteUsersToCurrentThread = apps.get_model('api', 'InviteUsersToCurrentThread')
        ShowTicketModal = apps.get_model('api', 'ShowTicketModal')
        ShowCustomModal = apps.get_model('api', 'ShowCustomModal')
        ShowSelectMenu = apps.get_model('api', 'ShowSelectMenu')
        TriggerCallback = apps.get_model('api', 'TriggerCallback')
        InviteUsersWithRoleToCurrentThread = apps.get_model('api', 'InviteUsersWithRoleToCurrentThread')

        handler_type = data['handler_type']

        if handler_type == EVENT_HANDLER_TYPE_GUIDED_FLOW:
            raise Exception("Guided flow should happen only once in import array on first position")

        if handler_type == EVENT_HANDLER_TYPE_TRIGGER_CALLBACK:
            return {
                "event_handler": TriggerCallback.objects.first(),
                "nested_events": []
            }
        if handler_type == EVENT_HANDLER_TYPE_GUIDED_FLOW_STEP:
            [step, buttons] = GuidedFlowStep.create_from_json(data, flow)
            return {
                "event_handler": step,
                "nested_events": buttons
            }
        if handler_type == EVENT_HANDLER_TYPE_DELETE_CURRENT_THREAD:
            return {
                "event_handler": DeleteCurrentThread.objects.first(),
                "nested_events": []
            }
        if handler_type == EVENT_HANDLER_TYPE_ARCHIVE_CURRENT_THREAD:
            return {
                "event_handler": ArchiveCurrentThread.objects.first(),
                "nested_events": []
            }
        if handler_type == EVENT_HANDLER_TYPE_SHOW_TICKET_MODAL:
            return {
                "event_handler": ShowTicketModal.create_from_json(data, flow),
                "nested_events": []
            }
        if handler_type == EVENT_HANDLER_TYPE_SHOW_CUSTOM_MODAL:
            return {
                "event_handler": ShowCustomModal.create_from_json(data, flow),
                "nested_events": []
            }
        if handler_type == EVENT_HANDLER_TYPE_SHOW_SELECT_MENU:
            [menu, options] = ShowSelectMenu.create_from_json(data, flow)
            return {
                "event_handler": menu,
                "nested_events": options
            }
        if handler_type == EVENT_HANDLER_TYPE_INVITE_USERS_TO_CURRENT_THREAD:
            return {
                "event_handler": InviteUsersToCurrentThread.create_from_json(data, flow),
                "nested_events": []
            }
        if handler_type == EVENT_HANDLER_TYPE_GRANT_ROLE:
            return {
                "event_handler": GrantRole.create_from_json(data, flow),
                "nested_events": []
            }
        if handler_type == EVENT_HANDLER_TYPE_INVITE_USERS_WITH_ROLE_TO_CURRENT_THREAD:
            return {
                "event_handler": InviteUsersWithRoleToCurrentThread.create_from_json(data, flow),
                "nested_events": []
            }
        if handler_type == EVENT_HANDLER_TYPE_SHOW_CAPTCHA:
            return {
                "event_handler": ShowCaptcha.create_from_json(data, flow),
                "nested_events": []
            }

    def to_json(self):
        DeleteCurrentThread = apps.get_model('api', 'DeleteCurrentThread')
        GuidedFlow = apps.get_model('api', 'GuidedFlow')
        GuidedFlowStep = apps.get_model('api', 'GuidedFlowStep')
        GrantRole = apps.get_model('api', 'GrantRole')
        ArchiveCurrentThread = apps.get_model('api', 'ArchiveCurrentThread')
        InviteUsersToCurrentThread = apps.get_model('api', 'InviteUsersToCurrentThread')
        ShowTicketModal = apps.get_model('api', 'ShowTicketModal')
        ShowCaptcha = apps.get_model('api', 'ShowCaptcha')
        ShowCustomModal = apps.get_model('api', 'ShowCustomModal')
        ShowSelectMenu = apps.get_model('api', 'ShowSelectMenu')
        TriggerCallback = apps.get_model('api', 'TriggerCallback')
        InviteUsersWithRoleToCurrentThread = apps.get_model('api', 'InviteUsersWithRoleToCurrentThread')

        event_handler = self.as_leaf_class()

        response = None

        if type(event_handler) == GuidedFlow:
            response = event_handler.abstractbotevent_ptr.to_json(with_triggered_handlers=True)
            response['handler_type'] = EVENT_HANDLER_TYPE_GUIDED_FLOW
            response['guided_flow_id'] = event_handler.id
        if type(event_handler) == TriggerCallback:
            response = event_handler.serialize_to_json()
        if type(event_handler) == GuidedFlowStep:
            response = event_handler.serialize_to_json()
        if type(event_handler) == GrantRole:
            response = event_handler.serialize_to_json()
        if type(event_handler) == DeleteCurrentThread:
            response = event_handler.serialize_to_json()
        if type(event_handler) == ArchiveCurrentThread:
            response = event_handler.serialize_to_json()
        if type(event_handler) == ShowTicketModal:
            response = event_handler.serialize_to_json()
        if type(event_handler) == ShowCaptcha:
            response = event_handler.serialize_to_json()
        if type(event_handler) == ShowCustomModal:
            response = event_handler.serialize_to_json()
        if type(event_handler) == ShowSelectMenu:
            response = event_handler.serialize_to_json()
        if type(event_handler) == InviteUsersToCurrentThread:
            response = event_handler.serialize_to_json()
        if type(event_handler) == InviteUsersWithRoleToCurrentThread:
            response = event_handler.serialize_to_json()

        response['event_handler_id'] = str(self.event_handler_id)

        return response

    class Meta:
        ordering = ["event_handler_id"]