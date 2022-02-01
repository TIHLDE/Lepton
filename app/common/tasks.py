from app.celery import app
from app.util.tasks import BaseTask


@app.task(bind=True, base=BaseTask)
def delete_old_log_entries(self, *args, **kwargs):
    from datetime import timedelta

    from django.contrib.admin.models import LogEntry

    from app.util.utils import now

    LogEntry.objects.filter(created_at_lte=now() - timedelta(days=30)).delete()
    self.logger.info("Log entries older than 30 days have been deleted")
