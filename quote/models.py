from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
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
    interval_minutes = models.IntegerField(default=60)  # Time interval for receiving quotes in minutes
    
    def get_scheduled_times(self):
        """
        Generate and return a list of times when notifications should be sent
        based on the user's time window and interval.
        """
        times = []
        
        # Get current date and ensure time zone aware
        current_date = timezone.localtime(timezone.now()).date()
        
        # Convert the start_time and end_time to datetime objects on the current date
        start_datetime = timezone.make_aware(datetime.combine(current_date, self.start_time))
        end_datetime = timezone.make_aware(datetime.combine(current_date, self.end_time))

        # Handle the case where end_time is actually on the next day (e.g., 10 PM to 2 AM)
        if end_datetime < start_datetime:
            # If end_time is earlier than start_time, we add a day to the end_time
            end_datetime += timedelta(days=1)

        # Generate scheduled times based on the interval
        current_time = start_datetime
        while current_time < end_datetime:
            times.append(current_time)
            current_time += timedelta(minutes=self.interval_minutes)

        return times
    

    
