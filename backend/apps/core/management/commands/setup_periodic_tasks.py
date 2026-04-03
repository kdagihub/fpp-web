import json

from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask, CrontabSchedule


class Command(BaseCommand):
    help = "Enregistre les tâches périodiques Celery Beat dans la base."

    def handle(self, *args, **options):
        schedule_3am, _ = CrontabSchedule.objects.get_or_create(
            minute="0", hour="3", day_of_week="*",
            day_of_month="*", month_of_year="*",
        )
        schedule_4am, _ = CrontabSchedule.objects.get_or_create(
            minute="0", hour="4", day_of_week="*",
            day_of_month="*", month_of_year="*",
        )
        schedule_6am, _ = CrontabSchedule.objects.get_or_create(
            minute="0", hour="6", day_of_week="*",
            day_of_month="*", month_of_year="*",
        )

        tasks = [
            {
                "name": "Cleanup expired user sessions (daily 3AM)",
                "task": "apps.user_sessions.tasks.cleanup_expired_sessions",
                "crontab": schedule_3am,
            },
            {
                "name": "Flush expired blacklisted tokens (daily 4AM)",
                "task": "apps.core.tasks.flush_expired_blacklisted_tokens",
                "crontab": schedule_4am,
            },
            {
                "name": "Rotate emergency purge codes (daily 6AM)",
                "task": "apps.emergency.tasks.rotate_emergency_codes",
                "crontab": schedule_6am,
            },
        ]

        for task_def in tasks:
            obj, created = PeriodicTask.objects.update_or_create(
                name=task_def["name"],
                defaults={
                    "task": task_def["task"],
                    "crontab": task_def["crontab"],
                    "enabled": True,
                },
            )
            status = "+" if created else "~"
            self.stdout.write(f"  {status} {task_def['name']}")

        self.stdout.write(self.style.SUCCESS("Tâches périodiques configurées."))
