import random

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.utils import timezone

from schedule_tasks.models import ScheduledTask, TaskExecutionHistory


class Command(BaseCommand):

    def create_user(self, username):
        log_tag = f"seed_tasks.create_user"
        User = get_user_model()
        user_details = {
            "email": f"{username}@email.com",
            "password": make_password("password"),
            "is_active": True
        }
        user, created = User.objects.get_or_create(username=username, defaults=user_details)
        if created:
            print(f"{log_tag} Created User '{username}' with password 'password'")
        else:
            print(f"{log_tag} User '{username}' already exists")
        return user

    def handle(self, *args, **options):

        log_tag = f"seed_tasks.handle"

        user_1 = self.create_user("user1")
        user_2 = self.create_user("user2")

        existing_scheduled_tasks = ScheduledTask.objects.filter(user_id__in=[user_1.id, user_2.id])
        if existing_scheduled_tasks:
            print(f"{log_tag} There are already {existing_scheduled_tasks.count()} tasks created. Abort seed tasks.")
            return

        print(f"{log_tag} Seeding Tasks...")

        scheduled_tasks = []
        for counter in range(100):
            task_data = {
                "title": f"Task {counter + 1}",
                "description": f"Descriptin for task {counter + 1}",
                "schedule_time": timezone.now() + timedelta(minutes=random.choice(list(range(0, 61, 5)))),
                "status": ScheduledTask.TaskStatus.SCHEDULED,
                "task_id_worker": "Dummy Tasks for Testing",
                "user": random.choice([user_1, user_2]),
            }
            scheduled_tasks.append(ScheduledTask(**task_data))
        ScheduledTask.objects.bulk_create(scheduled_tasks)
        print(f"{log_tag} Seeding Tasks Completed.")
