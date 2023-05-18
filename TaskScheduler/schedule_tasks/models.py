from django.conf import settings
from django.db import models


class ScheduledTask(models.Model):

    class TaskStatus:
        SCHEDULED = "scheduled"
        IN_PROGRESS = "in_progress"
        SUCCEEDED = "succeeded"
        FAILED = "failed"
        CANCELLED = "cancelled"

        CHOICES = (
            (SCHEDULED, "Scheduled"),
            (IN_PROGRESS, "In Progress"),
            (SUCCEEDED, "Succeeded"),
            (FAILED, "Failed"),
            (CANCELLED, "Cancelled"),
        )

    title = models.CharField(
        max_length=128,
        help_text="Name for the task",
    )
    description = models.TextField(
        help_text="Describe this task"
    )
    schedule_time = models.DateTimeField(
        help_text="Time at which the task should execute"
    )
    status = models.CharField(
        max_length=32,
        choices=TaskStatus.CHOICES,
        default=TaskStatus.SCHEDULED,
        help_text="Current state of the task",
    )
    task_id_worker = models.CharField(
        max_length=256,
        blank=True, null=True,
        help_text="ID provider by the async worker process"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="User who set this alert",
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class TaskExecutionHistory(models.Model):

    class TaskStatus:
        TRIGGERED = "triggered"
        SUCCEEDED = "succeeded"
        FAILED = "failed"
        CANCELLED = "cancelled"

        CHOICES = (
            (SUCCEEDED, "Succeeded"),
            (FAILED, "Failed"),
            (CANCELLED, "Cancelled"),
            (TRIGGERED, "Triggered"),
        )

    scheduled_task = models.ForeignKey(
        ScheduledTask,
        on_delete=models.CASCADE,
        help_text="A reference to the Scheduled Task",
    )
    task_id_worker = models.CharField(
        max_length=256,
        help_text="ID provider by the async worker process"
    )
    status = models.CharField(
        max_length=32,
        choices=TaskStatus.CHOICES,
        help_text="State of task"
    )
    failure_details = models.TextField(
        blank=True, null=True,
        help_text="Additional information regarding failure"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
