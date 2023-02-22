from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from api.models import GuidedFlowStep, User
import uuid

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    name = filename.split('.')[0]
    filename = "user-upload-%s-%s.%s" % (name, uuid.uuid4(), ext)
    return filename

class GuidedFlowStepUserUploadedFile(TimeStampedDeletableModel):
    name = models.TextField()

    step = models.ForeignKey(GuidedFlowStep, on_delete=models.SET_NULL, null=True,
                             related_name='uploaded_files')

    file = models.FileField(upload_to=get_file_path)

    discord_user_id = models.BigIntegerField()
    discord_username = models.TextField()

