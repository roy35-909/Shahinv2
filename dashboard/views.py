from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from shahin.base import NewAPIView
from django.core.paginator import Paginator, EmptyPage
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
from django.shortcuts import get_object_or_404
from authentication.models import Badge
from authentication.serializers import BadgeSerializer
from django.db.models import F
from datetime import timedelta
from django.utils import timezone
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
    permission_classes = [IsAdminUser]


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
    

class UserListView(APIView):
    '''
    <h1>Example Request for /dashboard/users/?page=1&page_size=5</h1>
    '''
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = User.objects.all().order_by('-created_at')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))

        paginator = Paginator(users, page_size)

        try:
            paginated_users = paginator.page(page)
        except EmptyPage:
            return Response({
                "detail": "No more users."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = UserListSerializer(paginated_users, many=True, context={'request': request})

        return Response({
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "results": serializer.data
        }, status=status.HTTP_200_OK)



class DeactivateAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request,pk):
        try:
            user = User.objects.get(id=pk)
        except:
            return Response({'error':'User Does Not Exist'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.id == user.id:
            return Response({'error':'You Are The User.'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = False
        user.save()
        return Response({"message": "Account deactivated successfully."}, status=status.HTTP_200_OK)

class ActivateAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request,pk):
        try:
            user = User.objects.get(id=pk)
        except:
            return Response({'error':'User Does Not Exist'}, status=status.HTTP_404_NOT_FOUND)
        user.is_active = True
        user.save()
        return Response({"message": "Account Activated successfully."}, status=status.HTTP_200_OK)



class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request,pk):
        try:
            user = User.objects.get(id=pk)
        except:
            return Response({'error':'User Does Not Exist'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({"message": "Account deleted successfully."}, status=status.HTTP_200_OK)
    

class NotificationListCreateView(NewAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = NotificationSerializer
    def get(self, request):
        notifications = Notifications.objects.all().order_by('-time')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationDetailView(NewAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = NotificationSerializer
    def get_object(self, pk):
        return get_object_or_404(Notifications, pk=pk)

    def get(self, request, pk):
        notification = self.get_object(pk)
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)

    def put(self, request, pk):
        notification = self.get_object(pk)
        serializer = NotificationSerializer(notification, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        notification = self.get_object(pk)
        notification.delete()
        return Response({'detail': 'Deleted successfully'}, status=status.HTTP_200_OK)
    

class BadgeListCreateView(NewAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = BadgeSerializer
    def get(self, request):
        badges = Badge.objects.all()
        serializer = BadgeSerializer(badges, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BadgeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BadgeDetailView(NewAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = BadgeSerializer
    def get_object(self, pk):
        return get_object_or_404(Badge, pk=pk)

    def get(self, request, pk):
        badge = self.get_object(pk)
        serializer = BadgeSerializer(badge)
        return Response(serializer.data)

    def put(self, request, pk):
        badge = self.get_object(pk)
        serializer = BadgeSerializer(badge, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        badge = self.get_object(pk)
        badge.delete()
        return Response({'detail': 'Badge deleted successfully'}, status=status.HTTP_200_OK)
    

class LeaderboardView(APIView):

    '''
    <h1>GET /?page=2&page_size=10</h1>
    '''

    permission_classes = [permissions.IsAdminUser]
    serializer_class = LeaderboardSerializer

    def get(self, request):
        # Get users, ordered by points
        users = User.objects.annotate(total_points=F('points')).order_by('-total_points')

        # Pagination setup
        page_size = request.query_params.get('page_size', 10)  # Default to 10 if not provided
        page_number = request.query_params.get('page', 1)  # Default to page 1 if not provided

        paginator = Paginator(users, page_size)  # Paginate users
        page = paginator.get_page(page_number)  # Get the page

        leaderboard_data = []
        for idx, user in enumerate(page.object_list):
            # Add rank (calculate based on pagination)
            rank = (page.number - 1) * paginator.per_page + idx + 1
            # Serialize the user and add the rank to the data
            serializer = LeaderboardSerializer(user, context={'request': request})
            leaderboard_data.append({'rank': rank, **serializer.data})

        # Return paginated response
        return Response({
            'count': paginator.count,
            'next': page.has_next(),
            'previous': page.has_previous(),
            'results': leaderboard_data
        }, status=200)

class DeleteUserFromLeaderboard(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()

        return Response({"detail": "User deleted successfully from leaderboard"}, status=status.HTTP_200_OK)
    
class PaymentListView(NewAPIView):
    
    '''
    <h1>GET /?page=2&page_size=10</h1>
    '''
    permission_classes = [permissions.IsAdminUser]
    serializer_class = PaymentSerializer
    def get(self, request):

        payments = Payment.objects.all()


        page_size = request.query_params.get('page_size', 10)  
        page_number = request.query_params.get('page', 1)  


        paginator = Paginator(payments, page_size)
        page = paginator.get_page(page_number)


        serializer = PaymentSerializer(page.object_list, many=True, context={'request': request})


        return Response({
            'count': paginator.count,
            'next': page.has_next(),
            'previous': page.has_previous(),
            'results': serializer.data
        }, status=200)
    
class PaymentDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        payment.delete()
        return Response({"detail": "Payment deleted successfully."}, status=status.HTTP_200_OK)
    

class SubscriptionPlanUpdateView(NewAPIView):
    '''
    <h2> Names Are </h2> \n
    monthly \n
    yearly \n
    lifetime \n
    '''
    permission_classes = [IsAdminUser]
    serializer_class = SubscriptionPlanSerializer
    def put(self, request, name):

        try:
            subscription_plan = SubscriptionPlan.objects.get(name=name)
        except SubscriptionPlan.DoesNotExist:
            return Response({"detail": "SubscriptionPlan not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubscriptionPlanSerializer(subscription_plan, data=request.data,context={'request': request},partial=True)

        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class SubscriptionPlanListView(NewAPIView):

    permission_classes = [IsAdminUser]
    serializer_class = SubscriptionPlanSerializer
    def get(self, request):

        subscription_plan = SubscriptionPlan.objects.all()

        serializer = SubscriptionPlanSerializerList(subscription_plan, many=True, context={'request': request})


        return Response(serializer.data, status=status.HTTP_200_OK)

    


class PrivacyPolicyAPIView(NewAPIView):

    permission_classes = [IsAdminUser]
    serializer_class = PrivacyPolicySerializer
    def post(self,request):

        data = request.data 
        if 'text' not in data:
            return Response({'error':'missing field text'}, status=status.HTTP_404_NOT_FOUND)
        
        privacy_policy = PrivacyPolicy.objects.all()

        if privacy_policy.exists():
            privacy_policy = privacy_policy.first()
            privacy_policy.text = data['text']
            privacy_policy.save()
        
        else:
            privacy_policy = PrivacyPolicy.objects.create(text = data['text'])
        
        ser = PrivacyPolicySerializer(privacy_policy)

        return Response(ser.data, status=status.HTTP_200_OK)
    
class TrimsAndConditionAPIView(NewAPIView):

    permission_classes = [IsAdminUser]
    serializer_class = TremsAndConditionSerializer
    def post(self,request):

        data = request.data 
        if 'text' not in data:
            return Response({'error':'missing field text'}, status=status.HTTP_404_NOT_FOUND)
        
        privacy_policy = TremsAndCondition.objects.all()

        if privacy_policy.exists():
            privacy_policy = privacy_policy.first()
            privacy_policy.text = data['text']
            privacy_policy.save()
        
        else:
            privacy_policy = PrivacyPolicy.objects.create(text = data['text'])

        ser = TremsAndConditionSerializer(privacy_policy)

        return Response(ser.data, status=status.HTTP_200_OK)
    

class PrivacyPolicyRetrieveAPIView(APIView):

    def get(self, request):
        try:
            privacy_policy = PrivacyPolicy.objects.get(id=1)
        except PrivacyPolicy.DoesNotExist:
            return Response({"detail": "PrivacyPolicy not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PrivacyPolicySerializer(privacy_policy)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TermsAndConditionRetrieveAPIView(APIView):

    def get(self, request):

        try:
            terms_and_condition = TremsAndCondition.objects.get(id=1)
        except TremsAndCondition.DoesNotExist:
            return Response({"detail": "TermsAndCondition not found."}, status=status.HTTP_404_NOT_FOUND)


        serializer = TremsAndConditionSerializer(terms_and_condition)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class ChangeUserSubscription(NewAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSubscriptionSerializer
    def post(self, request):


        data = request.data
        if 'subscription_type' not in data:
            return Response({'error':'subscription_type not found in request body'}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'user_id' not in data:
            return Response({'error':'user_id not found in request body'}, status=status.HTTP_400_BAD_REQUEST)
        subscription_type = data['subscription_type']

        try:
            user = User.objects.get(id=data['user_id'])
        except:
            return Response({'error':'Not User Found'}, status=status.HTTP_404_NOT_FOUND)
        user.subscription_type = subscription_type
        user.subscription_start = timezone.now()
        if subscription_type == 'monthly':
            user.subscription_end = timezone.now() + timedelta(days=30)
        elif subscription_type == 'yearly':
            user.subscription_end = timezone.now() + timedelta(days=365)
        elif subscription_type == 'lifetime':
            user.subscription_end = None

        # Need A Peroadic Task Here
        user.save()

        return Response({'success':'User Subscription Updated Successfully'})
