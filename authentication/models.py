from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField

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
    city = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    target = MultiSelectField(choices=CATEGORY_CHOICES, max_length=200, null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']
    objects = CustomUserManager()