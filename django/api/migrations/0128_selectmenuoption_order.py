# Generated by Django 3.2.9 on 2022-10-26 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0127_showticketmodal_modal_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='selectmenuoption',
            name='order',
            field=models.FloatField(null=True),
        ),
    ]
