# Generated by Django 3.2.9 on 2022-06-29 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0060_custommodalfield_showcustommodal'),
    ]

    operations = [
        migrations.AddField(
            model_name='showcustommodal',
            name='title',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='custommodalfield',
            name='style',
            field=models.TextField(choices=[('SHORT', 'SHORT'), ('LONG', 'LONG')], default='LONG'),
        ),
        migrations.AlterField(
            model_name='custommodalfield',
            name='type',
            field=models.TextField(choices=[('TEXT_INPUT', 'TEXT_INPUT')], default='TEXT_INPUT'),
        ),
    ]
