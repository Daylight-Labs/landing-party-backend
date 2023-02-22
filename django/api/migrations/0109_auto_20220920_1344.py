# Generated by Django 3.2.9 on 2022-09-20 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0108_community_kick_users_ignore_datetime_before_utc'),
    ]

    operations = [
        migrations.AddField(
            model_name='showcaptcha',
            name='label',
            field=models.TextField(blank=True, help_text='Not used by bot. Used only as a label in admin panel', null=True),
        ),
        migrations.AddField(
            model_name='showticketmodal',
            name='label',
            field=models.TextField(blank=True, help_text='Not used by bot. Used only as a label in admin panel', null=True),
        ),
    ]