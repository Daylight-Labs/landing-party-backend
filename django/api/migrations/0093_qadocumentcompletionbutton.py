# Generated by Django 3.2.9 on 2022-08-02 13:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0092_alter_selectmenuoption_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='QaDocumentCompletionButton',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True)),
                ('deleted_on', models.DateTimeField(blank=True, null=True)),
                ('label', models.TextField(max_length=80)),
                ('button_style', models.IntegerField(choices=[(1, 'Primary'), (2, 'Secondary'), (3, 'Success'), (4, 'Danger')], default=3, max_length=50)),
                ('qa_document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='completion_buttons', to='api.qadocument')),
                ('triggered_flow', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='qa_document_completion_buttons', to='api.guidedflow')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]
