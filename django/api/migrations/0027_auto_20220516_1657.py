# Generated by Django 3.2.9 on 2022-05-16 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_guidedflow_is_enabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qadocument',
            name='answer_jump_url',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='qadocument',
            name='question_jump_url',
            field=models.TextField(blank=True, null=True),
        ),
    ]
