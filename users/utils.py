from datetime import timedelta
from django.utils import timezone
from authentication.models import LoginHistory
from quote.models import UserQuote
def has_logged_in_seven_consecutive_days(user):
    today = timezone.now().date()

    seven_days_ago = today - timedelta(days=6)
    

    consecutive = LoginHistory.objects.filter(
        user=user,
        login_date__gte=seven_days_ago,
        login_date__lte=today
    ).order_by('login_date').count()

    


    print(consecutive)
    if consecutive >=7:
        return 100
    percentage = (consecutive/7)*100
    return percentage

def has_share_10_quote_on_social_media(user):

    number = UserQuote.objects.filter(user=user, is_share=True).count()

 

    # If we have 7 consecutive logins, return True
    if number >=10:
        return 100
    percentage = (number/10)*100
    return percentage
