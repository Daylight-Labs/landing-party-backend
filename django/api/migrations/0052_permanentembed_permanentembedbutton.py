# Generated by Django 3.2.9 on 2022-06-10 13:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0051_alter_guidedflow_community'),
    ]

    operations = [
        migrations.CreateModel(
            name='PermanentEmbed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True)),
                ('deleted_on', models.DateTimeField(blank=True, null=True)),
                ('channel_entrypoint_id', models.BigIntegerField(blank=True, default=None, null=True, unique=True)),
                ('community', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='permanent_embeds', to='api.community')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PermanentEmbedButton',
            fields=[
                ('abstractbotevent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='api.abstractbotevent')),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True)),
                ('deleted_on', models.DateTimeField(blank=True, null=True)),
                ('button_label', models.TextField()),
                ('button_style', models.IntegerField(choices=[(1, 'Primary'), (2, 'Secondary'), (3, 'Success'), (4, 'Danger')], default=3, max_length=50)),
                ('embed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='embed_buttons', to='api.permanentembed')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('api.abstractbotevent', models.Model),
        ),
    ]
