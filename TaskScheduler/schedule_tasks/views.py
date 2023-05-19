from rest_framework import status
from rest_framework.decorators import action
# from rest_framework.generics import (
#     ListCreateAPIView, RetrieveUpdateDestroyAPIView,
# )
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from schedule_tasks.models import ScheduledTask, TaskExecutionHistory
from schedule_tasks.serializers import (
    ScheduledTaskSerializer, TaskExecutionHistorySerializer,
    ScheduledTaskListParamsSerializer, ReScheduleTaskDataSerializer,
)
from schedule_tasks.utils.task_utils import cancel_scheduled_task


class ScheduledTaskViewSet(ModelViewSet):

    model = ScheduledTask
    permission_classes = [IsAuthenticated]
    serializer_class = ScheduledTaskSerializer

    def get_queryset(self):
        return ScheduledTask.objects.filter(user_id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        query_set = self.get_queryset()
        serializer_class = self.get_serializer_class()

        request_query_params_serializer = ScheduledTaskListParamsSerializer(data=request.query_params)
        if not request_query_params_serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=request_query_params_serializer.errors)
        request_query_params = request_query_params_serializer.data

        filter_params = {}

        task_status = request_query_params.get("status")
        if task_status:
            filter_params["status"] = task_status

        schedule_time_start = request_query_params.get("schedule_time_start")
        if schedule_time_start:
            filter_params["schedule_time__gte"] = schedule_time_start

        schedule_time_end = request_query_params.get("schedule_time_end")
        if schedule_time_end:
            filter_params["schedule_time__lt"] = schedule_time_end

        sort_by = request_query_params.get('sort_by', '-created')

        query_set = query_set.filter(**filter_params).order_by(sort_by)
        query_set = self.paginate_queryset(queryset=query_set)
        response_data = serializer_class(query_set, many=True).data

        return self.paginator.get_paginated_response(response_data)

    def update(self, request, *args, **kwargs):
        scheduled_task = self.get_object()
        if scheduled_task.status in [ScheduledTask.TaskStatus.IN_PROGRESS, ScheduledTask.TaskStatus.SUCCEEDED]:
            err_data = {"error": f"Cannot update task when it is {scheduled_task.status}"}
            return Response(status=status.HTTP_400_BAD_REQUEST, data=err_data)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["get"])
    def history(self, request, pk):
        scheduled_task = self.get_object()
        history_query_set = scheduled_task.taskexecutionhistory_set.all().exclude(
            status=TaskExecutionHistory.TaskStatus.TRIGGERED
        ).order_by('-created')
        history_query_set = self.paginate_queryset(queryset=history_query_set)
        response_data = TaskExecutionHistorySerializer(history_query_set, many=True).data
        return self.paginator.get_paginated_response(response_data)

    @action(detail=True, methods=["patch"])
    def cancel(self, request, pk):
        scheduled_task = self.get_object()
        if scheduled_task.status not in [ScheduledTask.TaskStatus.SCHEDULED, ScheduledTask.TaskStatus.IN_PROGRESS]:
            err_data = {"error": "Only scheduled and in progress tasks can be cancelled"}
            return Response(status=status.HTTP_400_BAD_REQUEST, data=err_data)
        cancel_scheduled_task(scheduled_task)
        scheduled_task.refresh_from_db()
        response_data = self.get_serializer_class()(scheduled_task).data
        return Response(status=status.HTTP_200_OK, data=response_data)

    @action(detail=True, methods=["patch"])
    def reschedule(self, request, pk):
        scheduled_task = self.get_object()
        if scheduled_task.status not in [ScheduledTask.TaskStatus.FAILED, ScheduledTask.TaskStatus.CANCELLED]:
            err_data = {"error": "Only failed and cancelled tasks can be rescheduled"}
            return Response(status=status.HTTP_400_BAD_REQUEST, data=err_data)
        serializer = ReScheduleTaskDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        scheduled_task.schedule_time = serializer.data['schedule_time']
        scheduled_task.task_id_worker = None
        scheduled_task.status = ScheduledTask.TaskStatus.SCHEDULED
        scheduled_task.save()
        response_data = self.get_serializer_class()(scheduled_task).data
        return Response(status=status.HTTP_200_OK, data=response_data)


# class TaskListCreateAPIView(ListCreateAPIView):

#     permission_classes = [IsAuthenticated]
#     serializer_class = ScheduledTaskSerializer

#     def get_queryset(self):
#         return ScheduledTask.objects.filter(user_id=self.request.user.id)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

#     def list(self, request, *args, **kwargs):
#         query_set = self.get_queryset()
#         serializer_class = self.get_serializer_class()

#         request_query_params_serializer = ScheduledTaskListParamsSerializer(data=request.query_params)
#         if not request_query_params_serializer.is_valid():
#             return Response(status=status.HTTP_400_BAD_REQUEST, data=request_query_params_serializer.errors)
#         request_query_params = request_query_params_serializer.data

#         filter_params = {}

#         task_status = request_query_params.get("status")
#         if task_status:
#             filter_params["status"] = task_status

#         schedule_time_start = request_query_params.get("schedule_time_start")
#         if schedule_time_start:
#             filter_params["schedule_time__gte"] = schedule_time_start

#         schedule_time_end = request_query_params.get("schedule_time_end")
#         if schedule_time_end:
#             filter_params["schedule_time__lt"] = schedule_time_end

#         sort_by = request_query_params.get('sort_by', '-created')

#         query_set = query_set.filter(**filter_params).order_by(sort_by)
#         query_set = self.paginate_queryset(queryset=query_set)
#         response_data = serializer_class(query_set, many=True).data

#         return self.paginator.get_paginated_response(response_data)


# class TaskRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):

#     permission_classes = [IsAuthenticated]
#     serializer_class = ScheduledTaskSerializer

#     def get_queryset(self):
#         return ScheduledTask.objects.filter(user_id=self.request.user.id)

#     def update(self, request, *args, **kwargs):
#         task = self.get_object()
#         if task.status in [ScheduledTask.TaskStatus.IN_PROGRESS, ScheduledTask.TaskStatus.SUCCEEDED]:
#             err_data = {"error": f"Cannot update task when it is {task.status}"}
#             return Response(status=status.HTTP_400_BAD_REQUEST, data=err_data)
#         return super().update(request, *args, **kwargs)
