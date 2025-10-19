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
    schedule.all_schedule.all().delete()
    schedule.all_cornjobs.all().delete()
    schedule.save()
    scheduled_times = schedule.get_scheduled_times()
    print(f"Scheduled times: {scheduled_times}")


    for scheduled_time in scheduled_times:

        if scheduled_time.tzinfo is not None:
            scheduled_time = scheduled_time.replace(tzinfo=None)
        if now.tzinfo is not None:
            now = now.replace(tzinfo=None)
        crontab_schedule = CrontabSchedule.objects.create(
            minute=scheduled_time.minute,   # Set minute based on scheduled_time
            hour=scheduled_time.hour,       # Set hour based on scheduled_time
            day_of_week="*",                # Every day of the week
            day_of_month="*",               # Every day of the month
            month_of_year="*",              # Every month
        )


        task_name = f"send_motivational_quote_{user.id}_{scheduled_time.strftime('%Y-%m-%d_%H-%M-%S')}"
        
        periodic_task = PeriodicTask.objects.create(
            crontab=crontab_schedule,      
            name=task_name,                
            task="quote.tasks.send_motivation_quote",   
            args=f"[{user.id}]",           
            start_time=now,                
        )
        schedule.all_schedule.add(periodic_task)
        schedule.all_cornjobs.add(crontab_schedule)
        schedule.save()

      
        print(f"Scheduled periodic task for user {user.email} to run at {scheduled_time}, task ID: {periodic_task.id}")