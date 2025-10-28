from django.db import models




class Notifications(models.Model):
    USER_CHOICES = [
        ('all_user', 'All_User'),
        ('free', 'Free'),
        ('premium', 'Premium'),

    ]
    title = models.CharField(max_length=255)
    descriptions = models.TextField(max_length=500)
    time = models.DateTimeField()
    users = models.CharField(max_length=255, choices=USER_CHOICES, null=True, blank=True)


    def __str__(self):
        return self.title



class PrivacyPolicy(models.Model):
    text = models.TextField(max_length=2000)


class TremsAndCondition(models.Model):
    text = models.TextField(max_length=2000)


    
    



