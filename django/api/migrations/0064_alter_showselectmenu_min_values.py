# Generated by Django 3.2.9 on 2022-06-30 15:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0063_auto_20220630_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='showselectmenu',
            name='min_values',
            field=models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(25), django.core.validators.MinValueValidator(1)]),
        ),
    ]