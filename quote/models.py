from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
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
        current_time = datetime.combine(datetime.today(), self.start_time)
        end_time = datetime.combine(datetime.today(), self.end_time)

        while current_time < end_time:
            times.append(current_time)
            current_time += timedelta(minutes=self.interval_minutes)

        return times