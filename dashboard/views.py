from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from shahin.base import NewAPIView

from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models.functions import ExtractMonth
from payment.models import Payment
import calendar
from django.utils.timezone import now
from django.db.models import Sum,Q,Count
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from quote.models import UserQuote
from django.utils.timezone import timedelta
User = get_user_model()
# Create your views here.
class AdminTokenObtainPairView(TokenObtainPairView):
    """
    API View for admin login
    """
    serializer_class = AdminTokenObtainPairSerializer


class RevenueReportAPIView(NewAPIView):
    """
    API to get month-wise revenue for a given year.
    If no year is provided, it uses the current year.

    <h1>GET dashboard/revenue_report/?year=2025</h1>
    """
    permission_classes=[IsAdminUser]
    serializer_class = MonthlyRevenueSerializer
    def get(self, request):
        year = request.query_params.get('year')
        if year:
            try:
                year = int(year)
            except ValueError:
                return Response({"error": "Invalid year"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            year = now().year


        payments = Payment.objects.filter(
            status='completed',
            created_at__year=year
        ).annotate(
            month=ExtractMonth('created_at')
        ).values('month').annotate(
            revenue=Sum('amount')
        ).order_by('month')


        revenue_dict = {p['month']: p['revenue'] or 0 for p in payments}
        data = []
        for i in range(1, 13):
            data.append({
                "month": calendar.month_name[i],
                "revenue": revenue_dict.get(i, 0)
            })

        serializer = MonthlyRevenueSerializer(data, many=True)
        return Response(serializer.data)
    

class DashboardAPIView(APIView):
    """
    API to return:
    - Total Revenue
    - Total Users
    - Total Active Users
    - Premium Conversion Rate (users who have made at least one premium payment)

    Example Output:
    {
    "total_revenue": 12500.00,
    "total_users": 150,
    "total_active_users": 120,
    "premium_conversion_percentage": 30.67
    }
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Total revenue from completed payments
        total_revenue = Payment.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0

        # Total users
        total_users = User.objects.count()

        # Active users
        total_active_users = User.objects.filter(is_active=True).count()

        # Premium conversion: users with at least one completed payment that is not free
        premium_users = User.objects.filter(
            payments__status='completed'
        ).exclude(payments__amount=0).distinct().count()

        premium_conversion = 0
        if total_users > 0:
            premium_conversion = (premium_users / total_users) * 100

        data = {
            "total_revenue": total_revenue,
            "total_users": total_users,
            "total_active_users": total_active_users,
            "premium_conversion_percentage": round(premium_conversion, 2)
        }

        return Response(data, status=status.HTTP_200_OK)
    

class WeeklyUserQuoteActivityAPIView(APIView):
    """
    API to return daily user activity for the last 7 days,
    comparing Free vs Premium users, using day names.

    Example Output: \n
            [
        {
            "day": "Monday",
            "free_users_activity": 0,
            "premium_users_activity": 0
        },
        {
            "day": "Tuesday",
            "free_users_activity": 0,
            "premium_users_activity": 0
        },
        {
            "day": "Wednesday",
            "free_users_activity": 0,
            "premium_users_activity": 0
        },
        {
            "day": "Thursday",
            "free_users_activity": 0,
            "premium_users_activity": 0
        },
        {
            "day": "Friday",
            "free_users_activity": 0,
            "premium_users_activity": 0
        },
        {
            "day": "Saturday",
            "free_users_activity": 0,
            "premium_users_activity": 0
        },
        {
            "day": "Sunday",
            "free_users_activity": 0,
            "premium_users_activity": 3
        }
        ]
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = now().date()
        week_ago = today - timedelta(days=6)  

        activity_data = []
        for i in range(7):
            day = week_ago + timedelta(days=i)
            day_name = day.strftime('%A') 


            free_activity_count = UserQuote.objects.filter(
                user__is_active=True,
                user__payments__status='completed'
            ).exclude(
                user__payments__amount__gt=0
            ).filter(
                sent_at__date=day
            ).count()


            premium_activity_count = UserQuote.objects.filter(
                user__is_active=True,
                user__payments__status='completed',
                user__payments__amount__gt=0
            ).filter(
                sent_at__date=day
            ).count()

            activity_data.append({
                "day": day_name,
                "free_users_activity": free_activity_count,
                "premium_users_activity": premium_activity_count
            })

        return Response(activity_data)
    


class SubscriptionDistributionAPIView(APIView):
    """
    API to return percentage distribution of user subscription types.
    Example Output: \n
            {
        "total_users": 4,
        "distribution": [
            {
            "subscription_type": "Free",
            "count": 3,
            "percentage": 75
            },
            {
            "subscription_type": "Premium Monthly",
            "count": 1,
            "percentage": 25
            },
            {
            "subscription_type": "Premium Yearly",
            "count": 0,
            "percentage": 0
            },
            {
            "subscription_type": "Lifetime Premium",
            "count": 0,
            "percentage": 0
            }
        ]
        }
    """

    def get(self, request):
        # Count users by subscription type
        subscription_counts = (
            User.objects.values('subscription_type')
            .annotate(count=Count('id'))
        )

        total_users = User.objects.count() or 1  # avoid division by zero

        # Prepare result
        distribution = []
        for choice, label in User.SUBSCRIPTION_CHOICES:
            count = next(
                (item['count'] for item in subscription_counts if item['subscription_type'] == choice),
                0
            )
            percentage = round((count / total_users) * 100, 2)
            distribution.append({
                "subscription_type": label,
                "count": count,
                "percentage": percentage
            })

        return Response({
            "total_users": total_users,
            "distribution": distribution
        })