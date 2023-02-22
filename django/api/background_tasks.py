from background_task import background
from api.utils.spreadsheet_util import run_spreadsheet_migrations

@background(schedule=1)
def background_task_run_spreadsheet_migrations_now():
    from background_task.models import Task
    from api.background_tasks import background_task_run_spreadsheet_migrations_now

    task_to_leave = Task.objects.order_by('-run_at').first()
    # Remove duplicate tasks (due to multiple servers)
    for task in Task.objects.order_by('run_at'):
        if task.run_at >= task_to_leave.run_at:
            break
        task.delete()

    run_spreadsheet_migrations()