from celery import shared_task
from .models import User, UserQuote, Quote
from random import choice
# from .push_notification import send_push_notification  # Assume this function sends notifications

@shared_task
def send_motivation_quote(user_id):
    """
    Sends a quote to the user.
    """
    user = User.objects.get(id=user_id)

    # Get relevant quote for the user
    quote = get_relevant_quote(user)
    
    if quote:
        # Send the notification
        # send_push_notification(user, quote)
        print(f"Sending Push Notification to: {user} , {quote}")
        # Track sent quote
        UserQuote.objects.create(user=user, quote=quote)  # Track the sent quote

def get_relevant_quote(user):
    """
    Get a random relevant quote based on the user's interests.
    """
    user_targets = user.target
    available_quotes = Quote.objects.filter(category__in=user_targets)

    if available_quotes.exists():
        selected_quote = choice(available_quotes)
        if not UserQuote.objects.filter(user=user, quote=selected_quote).exists():
            return selected_quote
    return None