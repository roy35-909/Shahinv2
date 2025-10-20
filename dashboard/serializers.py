from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from authentication.models import UserBadge, LoginHistory
from .models import *
from payment.models import Payment, SubscriptionPlan
User = get_user_model()

class AdminTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer to allow only admin (is_staff) users to get JWT tokens
    """
    def validate(self, attrs):
        # Standard validation to get tokens
        data = super().validate(attrs)

        # Check if user is admin
        if not self.user.is_superuser:
            raise serializers.ValidationError(
                {'detail': 'You do not have admin privileges.'}
            )

        # Add extra user info if needed
        data.update({
            'user_id': self.user.id,
            'email': self.user.email,
            'is_superuser': self.user.is_superuser
        })
        return data
    

class MonthlyRevenueSerializer(serializers.Serializer):
    month = serializers.CharField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)

class UserListSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    join_date = serializers.DateTimeField(source='created_at', format="%Y-%m-%d %H:%M:%S")
    last_activity = serializers.DateTimeField(source='last_login', format="%Y-%m-%d %H:%M:%S", required=False)
    level = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'first_name', 'email', 'profile_photo', 'is_active', 'type', 'join_date', 'last_activity','level']

    def get_type(self, obj):
        return "Premium" if obj.subscription_type != 'free' else "Free"
    
    def get_level(self,obj):
        return 10
    



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = '__all__'


class LeaderboardSerializer(serializers.ModelSerializer):
    # rank = serializers.IntegerField()
    total_badges = serializers.SerializerMethodField()
    streak = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['first_name', 'profile_photo', 'points', 'total_badges', 'streak']

    def get_total_badges(self, obj):


        return UserBadge.objects.filter(user=obj, is_completed=True).count()

    def get_streak(self, obj):

        streak_days = LoginHistory.objects.filter(user=obj).order_by('-login_date')
        streak_count = 0
        last_login_date = None
        
        for login in streak_days:
            if last_login_date and (login.login_date - last_login_date).days == 1:
                streak_count += 1
            elif last_login_date is None:
                streak_count = 1
            last_login_date = login.login_date

        return streak_count
    

class PaymentSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    profile_photo = serializers.ImageField(source='user.profile_photo', required=False)
    email = serializers.EmailField(source='user.email')
    plan = serializers.CharField(source='user.subscription_type', required=False)

    class Meta:
        model = Payment
        fields = ['first_name', 'profile_photo', 'email', 'status', 'amount', 'payment_method', 'created_at','plan']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['price'] 



class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = ['text']

class TremsAndConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TremsAndCondition
        fields = ['text']