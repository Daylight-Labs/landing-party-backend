# Generated by Django 3.2.9 on 2022-07-08 15:06

import api.models.guided_flow_step_user_uploaded_file
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0067_auto_20220708_1034'),
    ]

    operations = [
        migrations.CreateModel(
            name='GuidedFlowStepUserUploadedFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True)),
                ('deleted_on', models.DateTimeField(blank=True, null=True)),
                ('name', models.TextField()),
                ('file', models.FileField(upload_to=api.models.guided_flow_step_user_uploaded_file.get_file_path)),
                ('discord_user_id', models.BigIntegerField()),
                ('discord_username', models.TextField()),
                ('step', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_files', to='api.guidedflowstep')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]
