# Generated by Django 3.2.9 on 2022-11-10 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0133_faqbotcreationobject_is_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='faqbotcreationobject',
            name='admin_role_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]