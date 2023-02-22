from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from api.models.qa_document import QaDocument
from api.models.guided_flow import GuidedFlow

import openai
import pickle

from api.models.user import User

BUTTON_STYLE_PRIMARY = 1
BUTTON_STYLE_SECONDARY = 2
BUTTON_STYLE_SUCCESS = 3
BUTTON_STYLE_DANGER = 4

class QaDocumentCompletionButton(TimeStampedDeletableModel):
    qa_document = models.ForeignKey(QaDocument,
                                    null=False,
                                    on_delete=models.CASCADE,
                                    related_name="completion_buttons")

    label = models.TextField(blank=False, max_length=80)

    button_style = models.IntegerField(max_length=50, choices=[
        (BUTTON_STYLE_PRIMARY, 'Primary'),
        (BUTTON_STYLE_SECONDARY, 'Secondary'),
        (BUTTON_STYLE_SUCCESS, 'Success'),
        (BUTTON_STYLE_DANGER, 'Danger')
    ], default=BUTTON_STYLE_SUCCESS)

    triggered_flow = models.ForeignKey(GuidedFlow,
                                       null=True,
                                       on_delete=models.CASCADE,
                                       related_name="qa_document_completion_buttons")