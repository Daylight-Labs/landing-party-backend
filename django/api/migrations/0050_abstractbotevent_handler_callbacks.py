# Generated by Django 3.2.9 on 2022-06-06 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0049_alter_guidedflow_abstractboteventhandler_ptr'),
    ]

    operations = [
        migrations.AddField(
            model_name='abstractbotevent',
            name='handler_callbacks',
            field=models.ManyToManyField(blank=True, related_name='callback_set_by', to='api.AbstractBotEventHandler'),
        ),
    ]
