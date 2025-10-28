from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def expire_subscription(user_id):
    try:
        user = User.objects.get(id=user_id)

        # Check if the subscription actually expired
        if user.subscription_end and user.subscription_end <= timezone.now():
            user.subscription_type = 'free'
            user.subscription_start = None
            user.subscription_end = None
            user.save()
            return f"User {user.email}'s subscription expired and set to free."
        else:
            return f"User {user.email}'s subscription not expired yet."
    except User.DoesNotExist:
        return f"User {user_id} not found."