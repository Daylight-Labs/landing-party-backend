# Generated by Django 3.2.9 on 2022-06-14 13:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0052_permanentembed_permanentembedbutton'),
    ]

    operations = [
        migrations.CreateModel(
            name='InviteUsersWithRoleToCurrentThread',
            fields=[
                ('abstractboteventhandler_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.abstractboteventhandler')),
                ('role_id', models.BigIntegerField(blank=True, default=None, null=True)),
            ],
            bases=('api.abstractboteventhandler',),
        ),
    ]
