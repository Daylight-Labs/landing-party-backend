# Generated by Django 3.2.9 on 2022-05-12 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_auto_20220512_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='guidedflow',
            name='channel_name',
            field=models.CharField(default='onboarding', max_length=50),
        ),
    ]
