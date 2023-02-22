from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from api.models import GuidedFlowStep
import uuid

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return filename

class GuidedFlowStepAttachedFile(TimeStampedDeletableModel):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to=get_file_path)
    step = models.ForeignKey(GuidedFlowStep, on_delete=models.SET_NULL, null=True,
                             related_name='attached_files')

    def copy(self, step):
        return GuidedFlowStepAttachedFile.objects.create(
            name=self.name,
            file=self.file,
            step=step
        )