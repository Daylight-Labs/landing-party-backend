# Generated by Django 3.2.9 on 2022-10-25 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0126_auto_20221025_1410'),
    ]

    operations = [
        migrations.AddField(
            model_name='showticketmodal',
            name='modal_title',
            field=models.TextField(default='Create a Ticket', max_length=45),
        ),
    ]
