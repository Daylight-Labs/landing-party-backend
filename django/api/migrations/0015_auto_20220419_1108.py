# Generated by Django 3.2.9 on 2022-04-19 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_merge_0013_eventlog_0013_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventlog',
            name='slackbot_log',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='eventlog',
            name='bot_response',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='eventlog',
            name='type',
            field=models.TextField(choices=[('QUESTION_WITH_DIRECT_ANSWER', 'QUESTION_WITH_DIRECT_ANSWER'), ('QUESTION_WITH_POTENTIAL_ANSWERS', 'QUESTION_WITH_POTENTIAL_ANSWERS'), ('QUESTION_WITHOUT_ANSWER', 'QUESTION_WITHOUT_ANSWER'), ('QUESTION_PROCESSING_RUNTIME_ERROR', 'QUESTION_PROCESSING_RUNTIME_ERROR')]),
        ),
        migrations.AlterField(
            model_name='eventlog',
            name='user_prompt',
            field=models.TextField(null=True),
        ),
    ]