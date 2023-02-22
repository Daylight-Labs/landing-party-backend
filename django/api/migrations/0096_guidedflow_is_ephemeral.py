# Generated by Django 3.2.9 on 2022-08-04 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0095_captcharequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='guidedflow',
            name='is_ephemeral',
            field=models.BooleanField(default=False, help_text='If not checked, channels/threads are used (depending on guild boost lvl)'),
        ),
    ]