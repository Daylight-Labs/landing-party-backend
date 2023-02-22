# Generated by Django 3.2.9 on 2022-08-15 15:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0098_qadocument_revision_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='notifications_channel_ref',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='is_notification_channel_for_community', to='api.discordchannel'),
        ),
    ]
