# Generated by Django 3.2.9 on 2022-05-30 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_remove_guidedflow_initial_step'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abstractbotevent',
            name='triggered_handlers',
            field=models.ManyToManyField(blank=True, related_name='triggered_by', to='api.AbstractBotEventHandler'),
        ),
    ]
