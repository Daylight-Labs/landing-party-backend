# Generated by Django 3.2.9 on 2022-10-03 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0113_auto_20221002_2202'),
    ]

    operations = [
        migrations.AddField(
            model_name='showcaptcha',
            name='captcha_type',
            field=models.CharField(choices=[('MA', 'Math'), ('TE', 'Text')], default='MA', max_length=2),
        ),
    ]
