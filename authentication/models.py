from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField
from django.utils import timezone
class CustomUserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError(_('Please enter an email address'))

        email=self.normalize_email(email)

        new_user=self.model(email=email,**extra_fields)

        new_user.set_password(password)

        new_user.save()

        return new_user


    def create_superuser(self,email,password,**extra_fields):

        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True'))


        return self.create_user(email=email,username=email,password=password,**extra_fields)


class User(AbstractUser):
    CATEGORY_CHOICES = [
        ('fitness', 'Fitness'),
        ('career', 'Career'),
        ('business', 'Business'),
        ('discipline', 'Discipline'),
        ('mindset', 'Mindset'),
    ]
    SUBSCRIPTION_CHOICES = [
        ('free', 'Free'),
        ('monthly', 'Premium Monthly'),
        ('yearly', 'Premium Yearly'),
        ('lifetime', 'Lifetime Premium'),
    ]
    email = models.EmailField(verbose_name='Email', max_length=255, unique=True)
    password = models.CharField(max_length=100)
    phone = models.CharField(max_length=20,null=True)
    otp = models.CharField(max_length=50,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    password_forget_token = models.CharField(max_length=300,null=True,blank=True)
    profile_photo = models.ImageField(
        upload_to="profile_photos/", null=True, blank=True
    )
    friends = models.ManyToManyField(
        'self', 
        through='Friendship',  # This specifies a through model for additional data
        symmetrical=False,     # False because friendship is typically not symmetrical
        related_name='friend_set',  # This allows you to access the friends from the reverse side
        blank=True              # Allow this relationship to be empty
    )
    subscription_type = models.CharField(
        max_length=20, choices=SUBSCRIPTION_CHOICES, default='free'
    )
    subscription_start = models.DateTimeField(null=True, blank=True)
    subscription_end = models.DateTimeField(null=True, blank=True)
    stripe_customer_id = models.CharField(
        max_length=255, null=True, blank=True
    )
    points = models.IntegerField(default=0)
    city = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    target = MultiSelectField(choices=CATEGORY_CHOICES, max_length=200, null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']
    objects = CustomUserManager()

class Friendship(models.Model):

    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]
    
    user1 = models.ForeignKey(User, related_name='friendship_1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='friendship_2', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user1.email} and {self.user2.email} - {self.status}'
    
    class Meta:
        unique_together = ('user1', 'user2') 

    def send_request(self):
        """Send a friend request from user1 to user2."""
        if self.status == self.PENDING:
            return "Friend request already sent."
        self.status = self.PENDING
        self.save()

    def accept_request(self):
        """Accept a friend request and create a mutual friendship."""
        if self.status != self.PENDING:
            return "Cannot accept a request that is not pending."
        self.status = self.ACCEPTED
        self.save()
        # Create mutual friendship (add both users to each other's friends)
        self.user1.friends.add(self.user2)
        self.user2.friends.add(self.user1)

    def reject_request(self):
        """Reject a friend request."""
        if self.status != self.PENDING:
            return "Cannot reject a request that is not pending."
        self.status = self.REJECTED
        self.save()
    
    def cancel_request(self):
        """Cancel a friend request if it's pending."""
        if self.status != self.PENDING:
            return "Cannot cancel a request that is not pending."
        self.delete()


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.email} logged in on {self.login_date}"
    

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    points_required = models.IntegerField()   
    image = models.ImageField(upload_to="badge_images/", null=True, blank=True)  

    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.badge.name}"

    def calculate_completion(self):
        """
        Calculate the badge completion percentage.
        Completion is based on points and level requirements.
        """
        points_progress = (self.points_earned / self.badge.points_required) * 100
        average_progress = points_progress 

        return average_progress