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
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'profile_photo']