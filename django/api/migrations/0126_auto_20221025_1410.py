# Generated by Django 3.2.9 on 2022-10-25 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0125_community_kick_users_who_joined_but_did_not_verify_after_hours'),
    ]

    operations = [
        migrations.AddField(
            model_name='showticketmodal',
            name='describe_label',
            field=models.TextField(default='Please describe your issue', max_length=45),
        ),
        migrations.AddField(
            model_name='showticketmodal',
            name='describe_placeholder',
            field=models.TextField(default='Please describe your issue', max_length=100),
        ),
        migrations.AddField(
            model_name='showticketmodal',
            name='subject_label',
            field=models.TextField(default='Subject', max_length=45),
        ),
        migrations.AddField(
            model_name='showticketmodal',
            name='subject_placeholder',
            field=models.TextField(default='Subject', max_length=100),
        ),
    ]