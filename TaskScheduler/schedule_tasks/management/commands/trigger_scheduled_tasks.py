import time
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from schedule_tasks.models import ScheduledTask
from schedule_tasks.utils.task_utils import trigger_scheduled_task


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Ideally this would be a cron. Simulating it with a while true
        while True:
            five_min_from_now = timezone.now() + timedelta(minutes=5)

            scheduled_tasks_to_trigger = ScheduledTask.objects.filter(
                status=ScheduledTask.TaskStatus.SCHEDULED, schedule_time__lte=five_min_from_now,
            )

            for scheduled_task in scheduled_tasks_to_trigger:
                trigger_scheduled_task(scheduled_task)

            time.sleep(5 * 60)
