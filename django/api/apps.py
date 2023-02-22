from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        from django.db.migrations.recorder import MigrationRecorder

        if not MigrationRecorder.Migration.objects.filter(app='background_task').exists():
            # Docker build fix (don't run backgrounnd task until background task migration is applied)
            return

        from background_task.models import Task
        from api.background_tasks import background_task_run_spreadsheet_migrations_now

        if Task.objects.count() == 0:
            background_task_run_spreadsheet_migrations_now(repeat=Task.HOURLY)
        else:
            # Tasks were created earlier
            pass