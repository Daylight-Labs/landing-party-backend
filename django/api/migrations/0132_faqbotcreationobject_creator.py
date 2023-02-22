# Generated by Django 3.2.9 on 2022-11-10 00:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0131_rename_channel_id_faqbotcreationobject_channel_ids'),
    ]

    operations = [
        migrations.AddField(
            model_name='faqbotcreationobject',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='faq_bot_creation_objects', to=settings.AUTH_USER_MODEL, to_field='discord_user_id'),
        ),
    ]