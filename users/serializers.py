from rest_framework import serializers
from django.db.models import QuerySet
from djoser.serializers import UserCreateSerializer
from authentication.models import User,Badge,UserBadge
from authentication.serializers import BadgeSerializer
from .utils import *
from .models import Support
class UserBadgeSerializer(serializers.ModelSerializer):
    completion_percentage = serializers.SerializerMethodField()
    badge = BadgeSerializer()
    class Meta:
        model = UserBadge
        fields = ['user', 'badge', 'is_completed', 'completion_percentage']

    def get_completion_percentage(self, obj):
        """
        Calculate the completion percentage based on the points.
        This will be based on the points the user has earned vs the points required for the badge.
        """
        points_earned = obj.user.points  
        points_required = obj.badge.points_required

        if points_required == 0: 
            return 100 if points_earned > 0 else 0
        
        percentage = (points_earned / points_required) * 100
        # if obj.badge.name == 'Tracker':
        #     other_critaria_percentage = has_logged_in_seven_consecutive_days(obj.user)
        #     percentage = min(percentage,100)
        #     print(f"User Points is {percentage}")
        #     print(f"Other Percentage is {other_critaria_percentage}")
        #     percentage = (percentage+other_critaria_percentage)/2
        #     return min(int(percentage),100)
        # if obj.badge.name == 'Hunter':
        #     other_critaria_percentage = has_share_10_quote_on_social_media(obj.user)
        #     percentage = min(percentage,100)
        #     percentage = (percentage+other_critaria_percentage)/2
        #     return min(int(percentage),100)
        return min(int(percentage), 100)
    
class UserProfilePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["profile_photo"]



class UserUpdateSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["first_name", "email", "points", "level","profile_photo","phone","subscription_type"]

    def get_level(self, obj):
        return int(obj.points/20) if obj.points else None


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)
    retype_password = serializers.CharField(write_only=True, min_length=6)

class SupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Support
        fields = ['id', 'email', 'description', 'file']

        