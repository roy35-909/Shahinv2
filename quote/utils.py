# utils.py

from datetime import datetime, timedelta
from .tasks import send_motivation_quote
from django.utils import timezone
from .models import UserSchedule

def schedule_user_notifications(user):
    # Get the current time (aware datetime)
    now = timezone.localtime(timezone.now())  # Convert to naive datetime (local time)
    
    # Get the user's schedule (for example)
    schedule = UserSchedule.objects.get(user=user)
    scheduled_times = schedule.get_scheduled_times()

    for scheduled_time in scheduled_times:
        # Ensure both are naive datetimes (either both aware or both naive)
        if scheduled_time.tzinfo is not None:
            scheduled_time = scheduled_time.replace(tzinfo=None)  # Convert to naive if aware

        # Ensure now is also naive
        if now.tzinfo is not None:
            now = now.replace(tzinfo=None)  # Convert to naive if aware

        # Calculate the delay for scheduling notifications
        delay = (scheduled_time - now).total_seconds()

        # Ensure delay is positive (only schedule future notifications)
        if delay > 0:
            # Schedule the notification here (for example, with Celery)
            send_motivation_quote.apply_async(args=[user.id], countdown=delay)
            print(f"Scheduled quote for user {user.email} at {scheduled_time}")
