# Generated by Django 3.2.9 on 2022-06-23 12:03

from django.db import migrations, models
import django.db.models.deletion


def migrate_singleton_to_instances(apps, schema_editor):
    ShowTicketModal = apps.get_model("api", "ShowTicketModal")
    AbstractBotEvent = apps.get_model("api", "AbstractBotEvent")
    AbstractBotEventHandler = apps.get_model("api", "AbstractBotEventHandler")

    assert len(ShowTicketModal.objects.all()) == 1

    singleton = ShowTicketModal.objects.first()

    for triggered_by in singleton.triggered_by.all():
        triggered_by.triggered_handlers.remove(singleton)
        event = AbstractBotEvent.objects.create()
        event_handler = AbstractBotEventHandler.objects.create()
        new_obj = ShowTicketModal.objects.create(abstractbotevent_ptr_id=event.event_id,
                                                 abstractboteventhandler_ptr_id=event_handler.event_handler_id)
        triggered_by.triggered_handlers.add(new_obj)

    singleton.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0058_alter_showticketmodal_abstractbotevent_ptr'),
    ]

    operations = [
        migrations.RunPython(migrate_singleton_to_instances)
    ]