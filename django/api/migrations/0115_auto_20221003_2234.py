# Generated by Django 3.2.9 on 2022-10-03 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0114_showcaptcha_captcha_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onboardingflowcreationobject',
            name='channel_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='onboardingflowcreationobject',
            name='guild_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='onboardingflowcreationobject',
            name='role_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
