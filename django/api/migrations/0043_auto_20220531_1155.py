# Generated by Django 3.2.9 on 2022-05-31 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0042_alter_abstractbotevent_triggered_handlers'),
    ]

    operations = [
        migrations.AddField(
            model_name='guidedflow',
            name='channel_entrypoint_id',
            field=models.BigIntegerField(blank=True, default=None, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='guidedflow',
            name='slash_command_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
