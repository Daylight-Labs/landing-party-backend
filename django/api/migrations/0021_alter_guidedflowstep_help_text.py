# Generated by Django 3.2.9 on 2022-05-05 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_alter_guidedflowstepaction_triggered_next_step'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guidedflowstep',
            name='help_text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
