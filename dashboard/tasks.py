
import logging
from shlex import quote
from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Subquery
from shahin.firebase_utils import send_notification_to_tokens
from authentication.models import Device

@shared_task
def send_notification_to_user(users, title, body):
    """
    Send a notification to the specified users.
    """
    for i in users:
        device  = Device.objects.filter(user_id=i)
        tokens = device.values_list('device_token', flat=True)
        if tokens:
            send_notification_to_tokens(tokens=tokens, title=title, body=body)
   