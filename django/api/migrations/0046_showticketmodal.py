# Generated by Django 3.2.9 on 2022-06-02 17:34

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0045_merge_20220531_1315'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShowTicketModal',
            fields=[
                ('abstractboteventhandler_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.abstractboteventhandler')),
            ],
            bases=('api.abstractboteventhandler',),
        )
    ]