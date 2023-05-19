import logging

from celery import states
from celery.result import AsyncResult
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from schedule_tasks.models import ScheduledTask, TaskExecutionHistory
from schedule_tasks.tasks import log_task_message

from TaskScheduler.celery import app

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


def cancel_scheduled_task(scheduled_task):
    log_tag = "schedule_tasks.utils.cancel_scheduled_task"
    if scheduled_task.status not in [ScheduledTask.TaskStatus.SCHEDULED, ScheduledTask.TaskStatus.IN_PROGRESS]:
        logger.error(f"{log_tag} Cannot cancel Scheduled Task {scheduled_task.id} with status {scheduled_task.status}")
        return

    logger.info(f"{log_tag} Canceling Scheduled Task {scheduled_task.id} with status {scheduled_task.status}")

    if scheduled_task.status == ScheduledTask.TaskStatus.IN_PROGRESS:
        task_result = AsyncResult(scheduled_task.task_id_worker, app=app)
        terminate = True if task_result.state == states.STARTED else False
        logger.info(
            f"{log_tag} Revoking task {scheduled_task.task_id_worker} for "
            f"Scheduled Task {scheduled_task.id} with terminate as {terminate}"
        )
        app.control.revoke(scheduled_task.task_id_worker, terminate=terminate)
    scheduled_task.status = ScheduledTask.TaskStatus.CANCELLED
    scheduled_task.save()
