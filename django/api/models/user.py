from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from easy_thumbnails.fields import ThumbnailerImageField

from api.model_managers.user_manager import UserManager

from api.models.community import Community

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('Email', null=True, unique=True, blank=True)

    discord_user_id = models.BigIntegerField(null=True, unique=True, blank=True)
    discord_username = models.TextField(null=True, blank=True)
    discord_avatar_hash = models.TextField(null=True, blank=True)

    date_registered =  models.DateTimeField(auto_now_add=True, null=False, blank=True)

    is_superuser = models.BooleanField(default=False, null=False)

    # this field is needed to enable users to use Django admin UI
    is_staff = models.BooleanField(default=False)

    # this field is needed to use Django authentication
    is_active = models.BooleanField(default=False)

    EMAIL_FIELD = 'email'
    
    USERNAME_FIELD = 'email'

    objects = UserManager()

    class Meta:
        db_table = 'api_user'

    # TODO: Update the callees
    def get_managed_communities(self) -> [Community] :
        from api.models.user_roleset import UserRoleSet

        managed_communities = list(self.community_set.all())

        guilds_with_admin_role = Community.objects.filter(
            admin_role_ids__isnull=False
        ).exclude(
            admin_role_ids__exact=""
        )

        admin_roles_by_guild_id = {}

        for guild in guilds_with_admin_role:
            admin_roles_by_guild_id[guild.guild_id] = list(
                filter(lambda x: len(x) > 0, map(lambda x: x.strip(), guild.admin_role_ids.split(',')))
            )

        user_role_sets = UserRoleSet.objects.filter(user=self, community__in=guilds_with_admin_role)

        for roleset in user_role_sets:
            admin_role_ids = admin_roles_by_guild_id.get(roleset.community.guild_id, [])

            for role_id in roleset.role_ids:
                if str(role_id) in admin_role_ids:
                    managed_communities.append(roleset.community)
                    break

        return managed_communities

    # TODO: Update the callees
    def get_managed_community(self):
        communities = self.get_managed_communities()
        if len(communities) == 0:
            return None
        return communities[0]

    def is_managed_community(self, guild_id):
        print(f"is_managed_community: {guild_id}")
        community = Community.objects.filter(guild_id=guild_id).first()
        print(f"Community: {community}")
        if community:
            e = community.admins.filter(id=self.id).exists()
            print(f"e: {e}")
            return e
        return False
    
    def __str__(self):
        return f"{self.id} [{self.discord_user_id}] {self.discord_username or ''}"