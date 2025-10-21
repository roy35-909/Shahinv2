from rest_framework import serializers
from authentication.models import Friendship
from django.contrib.auth import get_user_model

User = get_user_model()

class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ['id','user1', 'user2', 'status', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        """Ensure that we are not sending requests to the same user."""
        if data['user1'] == data['user2']:
            raise serializers.ValidationError("A user cannot send a friend request to themselves.")
        return data
    

class SendFriendRequestSerializer(serializers.Serializer):

    user2_id = serializers.IntegerField()

class AcceptFriendRequestSerializer(serializers.Serializer):

    friendship_id = serializers.IntegerField()


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'profile_photo','points']


class LeaderboardUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    first_name = serializers.CharField()
    profile_photo = serializers.ImageField()
    subscription_type = serializers.CharField()
    total_points = serializers.IntegerField()



class UserBadgeSerializer(serializers.Serializer):
    badge_id = serializers.IntegerField(source="badge.id")
    badge_name = serializers.CharField(source="badge.name")
    is_completed = serializers.BooleanField()