# Generated by Django 3.2.9 on 2022-12-02 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0138_community_faq_bot_google_spreadsheet_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='kick_users_who_sent_spam_times',
            field=models.IntegerField(help_text="After user sent spam (see 'Is spam' field on QA doc) this number of times within last 7 days, user will be kicked", null=True),
        ),
        migrations.AddField(
            model_name='qadocument',
            name='is_spam',
            field=models.BooleanField(default=False, help_text="Used for kicking users for spamming (see 'Kick users after X spam messages within 7 days' field in community admin)"),
        ),
    ]
