# from django.urls import path

from rest_framework.routers import DefaultRouter

from schedule_tasks.views import (
    ScheduledTaskViewSet,
    # TaskListCreateAPIView, TaskRetrieveUpdateDestroyAPIView,
)

router = DefaultRouter()
router.register(r'', ScheduledTaskViewSet, basename='task_viewset')
urlpatterns = router.urls

# urlpatterns = [
    # path('', TaskListCreateAPIView.as_view(), name="list_create_tasks"),
    # path('<int:pk>', TaskRetrieveUpdateDestroyAPIView.as_view(), name="retrieve_update_destroy_tasks"),
# ]
