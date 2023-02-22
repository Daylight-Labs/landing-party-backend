from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage
from multicolorcaptcha import CaptchaGenerator

from io import BytesIO
from django.core.files.base import ContentFile

class CaptchaRequest(TimeStampedDeletableModel):

    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')

    equation_string = models.CharField(max_length=30)
    equation_result = models.CharField(max_length=30)

    image = models.ImageField(
        storage=S3Boto3Storage(bucket_name='bn-bot-capcha-resources')
    )