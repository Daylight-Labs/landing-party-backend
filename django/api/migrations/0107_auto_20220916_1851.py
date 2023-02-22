# Generated by Django 3.2.9 on 2022-09-16 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0106_onboardingflowcreationobject'),
    ]

    operations = [
        migrations.AddField(
            model_name='onboardingflowcreationobject',
            name='question_1',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='onboardingflowcreationobject',
            name='question_1_required',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='onboardingflowcreationobject',
            name='question_2',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='onboardingflowcreationobject',
            name='question_2_required',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='onboardingflowcreationobject',
            name='question_3',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='onboardingflowcreationobject',
            name='question_3_required',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='onboardingflowcreationobject',
            name='question_4',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='onboardingflowcreationobject',
            name='question_4_required',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='onboardingflowcreationobject',
            name='question_5',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='onboardingflowcreationobject',
            name='question_5_required',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='onboardingflowcreationobject',
            name='captcha',
            field=models.CharField(blank=True, choices=[('MA', 'Math'), ('TE', 'Text'), ('NO', 'None')], default='NO', max_length=2),
        ),
    ]