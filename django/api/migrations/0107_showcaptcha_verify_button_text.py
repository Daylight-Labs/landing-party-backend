# Generated by Django 3.2.9 on 2022-09-16 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0106_auto_20220915_1333'),
    ]

    operations = [
        migrations.AddField(
            model_name='showcaptcha',
            name='verify_button_text',
            field=models.TextField(blank=True, help_text="Default is 'Verify answer'", max_length=90, null=True),
        ),
    ]
