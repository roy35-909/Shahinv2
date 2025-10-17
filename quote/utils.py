# utils.py

import uuid
from django.utils import timezone
from .models import UserSchedule
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.utils import timezone
def schedule_user_notifications(user):
    # Get the current time (local time)
    now = timezone.localtime(timezone.now())

    # Get the user's schedule (for example)
    schedule = UserSchedule.objects.get(user=user)
    scheduled_times = schedule.get_scheduled_times()
    print(f"Scheduled times: {scheduled_times}")

    # Loop through all scheduled times for the user
    for scheduled_time in scheduled_times:
        # Ensure the scheduled time is a naive datetime (if it's timezone-aware)
        if scheduled_time.tzinfo is not None:
            scheduled_time = scheduled_time.replace(tzinfo=None)

        # Ensure `now` is naive (if it's timezone-aware)
        if now.tzinfo is not None:
            now = now.replace(tzinfo=None)

        # Convert the scheduled time into a CrontabSchedule (hour and minute)
        crontab_schedule = CrontabSchedule.objects.create(
            minute=scheduled_time.minute,   # Set minute based on scheduled_time
            hour=scheduled_time.hour,       # Set hour based on scheduled_time
            day_of_week="*",                # Every day of the week
            day_of_month="*",               # Every day of the month
            month_of_year="*",              # Every month
        )

        # Create the periodic task that uses the crontab schedule
        task_name = f"send_motivational_quote_{user.id}_{scheduled_time.strftime('%Y-%m-%d_%H-%M-%S')}"
        
        periodic_task = PeriodicTask.objects.create(
            crontab=crontab_schedule,      # Link to the crontab schedule
            name=task_name,                # Unique task name
            task="quote.tasks.send_motivation_quote",   # The task to run
            args=f"[{user.id}]",           # Arguments passed to the task (user.id)
            start_time=now,                # Start time (can be set to current time)
        )

        # Log the task creation
        print(f"Scheduled periodic task for user {user.email} to run at {scheduled_time}, task ID: {periodic_task.id}")