from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from easy_thumbnails.fields import ThumbnailerImageField
from django.contrib.postgres.fields import ArrayField

from api.model_managers.user_manager import UserManager

from api.models.community import Community
from api.models.user import User

class UserRoleSet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rolesets")
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="rolesets")

    role_ids = ArrayField(models.BigIntegerField(null=True, blank=True, unique=False))

    class Meta:
        unique_together = (("user", "community"),)