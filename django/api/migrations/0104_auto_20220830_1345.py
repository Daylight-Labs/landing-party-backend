# Generated by Django 3.2.9 on 2022-08-30 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0103_grantrole_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='showcaptcha',
            name='captcha_message',
            field=models.TextField(blank=True, max_length=1990, null=True),
        ),
        migrations.AddField(
            model_name='showcustommodal',
            name='csv_export_is_anonymous',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='showcustommodal',
            name='label',
            field=models.TextField(blank=True, help_text='Not used by bot. Used only as a label in admin panel', null=True),
        ),
        migrations.AddField(
            model_name='showselectmenu',
            name='csv_export_is_anonymous',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='showselectmenu',
            name='label',
            field=models.TextField(blank=True, help_text='Not used by bot. Used only as a label in admin panel', null=True),
        ),
    ]
