import logging

from datetime import timedelta
from django.utils import timezone

from schedule_tasks.models import ScheduledTask, TaskExecutionHistory
from schedule_tasks.tasks import log_task_message

logger = logging.getLogger(__name__)


def trigger_scheduled_task(scheduled_task):
    log_tag = "schedule_tasks.utils.trigger_scheduled_task"
    if scheduled_task.schedule_time > timezone.now() + timedelta(seconds=10*60):
        logger.error(
            f"{log_tag} Cannot trigger scheduled task {scheduled_task.id} to run at {scheduled_task.schedule_time}. "
            "Tasks can only be triggered within 10 min in future"
        )
        return
    logger.info(f"{log_tag} Triggering scheduled task {scheduled_task.id} to run at {scheduled_task.schedule_time}.")
    async_result = log_task_message.apply_async((scheduled_task.id, ), eta=scheduled_task.schedule_time)
    scheduled_task.task_id_worker = async_result.id
    scheduled_task.status = ScheduledTask.TaskStatus.IN_PROGRESS
    scheduled_task.save()
    TaskExecutionHistory.objects.create(
        scheduled_task_id=scheduled_task.id,
        task_id_worker=async_result.id,
        status=TaskExecutionHistory.TaskStatus.TRIGGERED,
    )
