# Generated by Django 3.2.9 on 2022-09-15 15:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0105_auto_20220913_1058'),
    ]

    operations = [
        migrations.CreateModel(
            name='OnboardingFlowCreationObject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True)),
                ('deleted_on', models.DateTimeField(blank=True, null=True)),
                ('captcha', models.CharField(choices=[('MA', 'Math'), ('TE', 'Text'), ('NO', 'None')], default='NO', max_length=2)),
                ('channel_id', models.BigIntegerField(null=True, unique=True)),
                ('role_id', models.BigIntegerField(null=True, unique=True)),
                ('guild_id', models.BigIntegerField(null=True, unique=True)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='onboarding_flow_creation_objects', to=settings.AUTH_USER_MODEL, to_field='discord_user_id')),
                ('flow', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.guidedflow')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]