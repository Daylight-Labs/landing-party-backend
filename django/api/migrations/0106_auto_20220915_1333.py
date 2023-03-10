# Generated by Django 3.2.9 on 2022-09-15 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0105_auto_20220913_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='kick_users_who_joined_but_did_not_verify_after_days',
            field=models.IntegerField(default=3),
        ),
        migrations.AddField(
            model_name='community',
            name='verified_role_id',
            field=models.BigIntegerField(blank=True, default=None, null=True),
        ),
    ]
