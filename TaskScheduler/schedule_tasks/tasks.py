import celery
import json
import logging
import random
import time

from schedule_tasks.models import ScheduledTask, TaskExecutionHistory
from TaskScheduler.celery import app

logger = logging.getLogger(__name__)


class ScheduleTaskHandler(celery.Task):

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        log_tag = "ScheduleTaskHandler.on_failure"
        schedule_task_id = args[0]
        TaskExecutionHistory.objects.create(
            scheduled_task_id=schedule_task_id,
            task_id_worker=task_id,
            status=TaskExecutionHistory.TaskStatus.FAILED,
            failure_details=json.dumps({
                'args': args,
                'kwargs': kwargs,
                'exception': str(exc),
                'traceback': str(einfo.traceback)
            })
        )
        task = ScheduledTask.objects.get(id=schedule_task_id)
        task.status = ScheduledTask.TaskStatus.FAILED
        task.save()
        logger.error(f"{log_tag} Scheduled Task with ID '{schedule_task_id}' failed with error ---> {exc}.")

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        log_tag = "ScheduleTaskHandler.on_retry"
        schedule_task_id = args[0]
        TaskExecutionHistory.objects.create(
            scheduled_task_id=schedule_task_id,
            task_id_worker=task_id,
            status=TaskExecutionHistory.TaskStatus.FAILED,
            failure_details=json.dumps({
                'args': args,
                'kwargs': kwargs,
                'exception': str(exc),
                'traceback': str(einfo.traceback)
            })
        )
        logger.error(f"{log_tag} Scheduled Task with ID '{schedule_task_id}' failed with error ---> {exc}. Retrying...")


    def on_success(self, retval, task_id, args, kwargs):
        log_tag = "ScheduleTaskHandler.on_success"
        schedule_task_id = args[0]
        TaskExecutionHistory.objects.create(
            scheduled_task_id=schedule_task_id,
            task_id_worker=task_id,
            status=TaskExecutionHistory.TaskStatus.SUCCEEDED,
        )
        task = ScheduledTask.objects.get(id=schedule_task_id)
        task.status = ScheduledTask.TaskStatus.SUCCEEDED
        task.save()
        logger.info(f"{log_tag} Scheduled Task with ID '{schedule_task_id}' completed succesfully")


@app.task(
    bind=True, base=ScheduleTaskHandler,
    autoretry_for=(Exception,), max_retries=5, retry_backoff=5, retry_jitter=True
)
def log_task_message(self, schedule_task_id):

    task = ScheduledTask.objects.get(id=schedule_task_id)

    if task.status == ScheduledTask.TaskStatus.SCHEDULED:
        task.status = ScheduledTask.TaskStatus.IN_PROGRESS
        task.save()

    if task.status != ScheduledTask.TaskStatus.IN_PROGRESS:
        return

    time.sleep(10)

    if random.choice([0, 1]):
        raise Exception("Simulate Failure")

    log_string = (
        f"\n==================================================================================\n\n"
        f"Scheduled Task ID: {schedule_task_id}\n"
        f"Title: {task.title}\n"
        f"Description: {task.description}\n"
        f"\n==================================================================================\n"
    )

    logger.info(log_string)
