from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from api.models import PermanentEmbed
import uuid

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "embed-%s.%s" % (uuid.uuid4(), ext)
    return filename

class PermanentEmbedAttachedFile(TimeStampedDeletableModel):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to=get_file_path)
    step = models.ForeignKey(PermanentEmbed, on_delete=models.SET_NULL, null=True,
                             related_name='attached_files')