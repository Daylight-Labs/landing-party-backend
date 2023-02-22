from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from api.models import GuidedFlowStep
from api.models.abstract_bot_event import AbstractBotEvent
from api.model_managers.deleted_objects_manager import ExcludeDeletedObjectsModelManager

BUTTON_STYLE_PRIMARY = 1
BUTTON_STYLE_SECONDARY = 2
BUTTON_STYLE_SUCCESS = 3
BUTTON_STYLE_DANGER = 4

ROW_CHOICES = zip( range(1,6), range(1,6) )

class GuidedFlowStepButton(AbstractBotEvent, TimeStampedDeletableModel):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')

    flow_step = models.ForeignKey(GuidedFlowStep, on_delete=models.CASCADE, related_name="step_buttons")
    button_label = models.TextField()
    button_style = models.IntegerField(max_length=50, choices=[
        (BUTTON_STYLE_PRIMARY, 'Primary'),
        (BUTTON_STYLE_SECONDARY, 'Secondary'),
        (BUTTON_STYLE_SUCCESS, 'Success'),
        (BUTTON_STYLE_DANGER, 'Danger')
    ], default=BUTTON_STYLE_SUCCESS)

    button_row = models.IntegerField(choices=ROW_CHOICES, null=True, blank=True)

    objects = ExcludeDeletedObjectsModelManager()

    def copy(self, flow_step):
        return GuidedFlowStepButton.objects.create(
            flow_step=flow_step,
            button_label=self.button_label,
            button_style=self.button_style,
            button_row=self.button_row
        )

