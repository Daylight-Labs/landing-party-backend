# Generated by Django 3.2.9 on 2022-08-17 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0099_community_notifications_channel_ref'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='admin_role_ids',
            field=models.TextField(blank=True, help_text='Comma separated role ids which will be considered admin roles by the bot', null=True),
        ),
    ]
