from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, CrontabSchedule
User = get_user_model()


class Quote(models.Model):
    content = models.TextField()
    category = models.CharField(choices=User.CATEGORY_CHOICES, max_length=20)
    author = models.CharField(max_length=255,default='Unknown')
    created_at = models.DateTimeField(auto_now_add=True)


class UserQuote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_liked = models.BooleanField(default=False)
    is_saved = models.BooleanField(default=False)
    is_share = models.BooleanField(default=False)
    

    class Meta:
        unique_together = ('user', 'quote')


class UserSchedule(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_time = models.TimeField(null=True,blank=True)  # e.g., 8 PM
    end_time = models.TimeField(null=True, blank=True)    # e.g., 12 AM
    interval_minutes = models.IntegerField(default=1)  # Time interval for receiving quotes in minutes
    all_schedule = models.ManyToManyField(PeriodicTask)
    all_cornjobs = models.ManyToManyField(CrontabSchedule)

    def get_scheduled_times(self):
        """
        Divide the time range between start_time and end_time equally
        into 'number_of_slots' parts and return the scheduled times.
        """
        times = []

        if not self.start_time or not self.end_time or self.interval_minutes <= 0:
            return times

        current_date = timezone.localtime(timezone.now()).date()
        start_datetime = timezone.make_aware(datetime.combine(current_date, self.start_time))
        end_datetime = timezone.make_aware(datetime.combine(current_date, self.end_time))

        # Handle overnight range (e.g., 10 PM to 2 AM)
        if end_datetime <= start_datetime:
            end_datetime += timedelta(days=1)

        total_duration = end_datetime - start_datetime
        interval = total_duration / self.interval_minutes

        # Generate equally divided times (excluding the end time)
        for i in range(self.interval_minutes):
            times.append(start_datetime + interval * i)

        return times
    

    
