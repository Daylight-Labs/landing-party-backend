from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from api.models import Community

class Tag(TimeStampedDeletableModel):

    name = models.CharField(max_length=30)
    qa_documents = models.ManyToManyField("QaDocument", related_name="tags")
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="tags")
