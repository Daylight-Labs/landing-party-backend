# Generated by Django 3.2.9 on 2022-03-07 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QaDocument',
            fields=[
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True)),
                ('deleted_on', models.DateTimeField(null=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('guild_id', models.IntegerField(db_index=True)),
                ('prompt', models.TextField()),
                ('completion', models.TextField()),
                ('model', models.TextField()),
                ('embedding_vector', models.TextField()),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]
