from django.contrib import admin

from schedule_tasks.models import ScheduledTask, TaskExecutionHistory


class TaskExecutionHistoryInlineAdmin(admin.StackedInline):
    model = TaskExecutionHistory
    readonly_fields = ("created", "updated", )
    extra = 0


class ScheduledTaskAdmin(admin.ModelAdmin):
    model = ScheduledTask
    inlines = [
        TaskExecutionHistoryInlineAdmin
    ]
    list_display = (
        "id", "user", "title", "status", "schedule_time",
        "created", "updated",
    )
    search_fields = (
        "title", "user__username", "description",
    )
    list_filter = (
        "status", "created",
    )
    readonly_fields = ("user", "created", "updated", )

    def save_model(self, request, obj, form, change):
        if not change:
            # the object is being created, so set the user
            obj.user = request.user
        obj.save()

    class Meta:
        ordering = ('-created',)


admin.site.register(ScheduledTask, ScheduledTaskAdmin)
