# Generated by Django 3.2.9 on 2022-10-04 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0115_auto_20221003_2234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onboardingflowcreationobject',
            name='captcha',
            field=models.CharField(choices=[('MA', 'Math'), ('TE', 'Text'), ('NO', 'None')], default='NO', max_length=2),
        ),
    ]
