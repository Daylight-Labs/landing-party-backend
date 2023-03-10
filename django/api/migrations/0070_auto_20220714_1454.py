# Generated by Django 3.2.9 on 2022-07-14 14:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0069_rename_discordchannel_botenableddiscordchannel'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='botenableddiscordchannel',
            options={},
        ),
        migrations.AlterField(
            model_name='botenableddiscordchannel',
            name='community',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bot_enabled_discord_channels', to='api.community'),
        ),
        migrations.AlterModelTable(
            name='botenableddiscordchannel',
            table='api_botenableddiscordchannnel',
        ),
    ]
