from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from schedule_tasks.models import ScheduledTask, TaskExecutionHistory


class TaskExecutionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskExecutionHistory
        fields = (
            "status", "created",
        )
        read_only_fields = fields
        ordering = ["-created"]


class ScheduledTaskSerializer(serializers.ModelSerializer):

    # history = TaskExecutionHistorySerializer(read_only=True, many=True, source="taskexecutionhistory_set")

    class Meta:
        model = ScheduledTask
        fields = (
            "id", "title", "description", "schedule_time", "status", "created", "updated",
        )
        read_only_fields = [
            "status", "created", "updated",
        ]
        ordering = ["-created"]

    def validate_schedule_time(self, schedule_time):
        if schedule_time <= timezone.now() or schedule_time > timezone.now() + timedelta(days=365):
            raise serializers.ValidationError("schedule_time within a year in the future")
        return schedule_time


class ScheduledTaskListParamsSerializer(serializers.Serializer):
    status = serializers.CharField(required=False)
    schedule_time_start = serializers.DateTimeField(required=False)
    schedule_time_end = serializers.DateTimeField(required=False)
    sort_by = serializers.CharField(required=False)

    def validate_status(self, status):
        task_status_choices = [
            task_status_choice[0] for task_status_choice in ScheduledTask.TaskStatus.CHOICES
        ]
        if status not in task_status_choices:
            err_msg = f"Invalid value '{status}' for status. Allowed values are {task_status_choices}"
            raise serializers.ValidationError(err_msg)
        return status

    def validate_sort_by(self, sort_by):
        sort_by_choices = ["schedule_time", "-schedule_time"]
        if sort_by not in sort_by_choices:
            err_msg = f"Invalid value '{sort_by}' for sort_by. Allowed values are {sort_by_choices}"
            raise serializers.ValidationError(err_msg)
        return sort_by

    def validate(self, data):
        data = super().validate(data)
        if (
            "schedule_time_start" in data and
            "schedule_time_end" in data and
            data["schedule_time_start"] >= data["schedule_time_end"]
        ):
            err_msg = "schedule_time_end must be greater than schedule_time_start"
            raise serializers.ValidationError(err_msg)
        return data
