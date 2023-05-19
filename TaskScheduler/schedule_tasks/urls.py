from rest_framework.routers import DefaultRouter

from schedule_tasks.views import ScheduledTaskViewSet

router = DefaultRouter()

router.register(r'', ScheduledTaskViewSet, basename='task_viewset')

urlpatterns = router.urls
