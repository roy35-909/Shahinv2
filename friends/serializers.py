from rest_framework import serializers
from authentication.models import Friendship
from django.contrib.auth import get_user_model
from django.db.models import Q
User = get_user_model()


class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ['id', 'user1', 'user2', 'status', 'created_at']
        read_only_fields = ['created_at']


class ListFriendRequestSerializer(serializers.ModelSerializer):
    friendship_id = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    profile_photo = serializers.SerializerMethodField()
    points = serializers.SerializerMethodField()
    class Meta:
        model = Friendship
        fields = ['friendship_id','user1', 'user2', 'status', 'created_at','first_name','profile_photo','points']
        read_only_fields = ['created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['status'] = 'request-sent' 
        return data
    
    def get_friendship_id(self,obj):
        return obj.id
    
    def get_first_name(self,obj):
        return obj.user1.first_name
    
    def get_profile_photo(self,obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.user1.profile_photo.url) if obj.user1.profile_photo else None
    def get_points(self,obj):
        return obj.user1.points


class SendFriendRequestSerializer(serializers.Serializer):

    user2_id = serializers.IntegerField()

class AcceptFriendRequestSerializer(serializers.Serializer):

    friendship_id = serializers.IntegerField()


class UserSearchSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    friendship_id = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id','friendship_id', 'first_name', 'profile_photo','status','points']

    def get_status(self, obj):
        request = self.context.get('request', None)
        if not request or not hasattr(request, 'user'):
            return None

        current_user = request.user

        # Try both directions: user1 -> user2 or user2 -> user1
        friendship = Friendship.objects.filter(
            Q(user1=current_user, user2=obj) | Q(user1=obj, user2=current_user)
        ).first()

        if not friendship:
            return "not-friend"

        # If friendship exists, check direction and status
        if friendship.status == "pending":
            if friendship.user1 == current_user:
                return "request-sent"
            elif friendship.user2 == current_user:
                return "request-received"

        elif friendship.status == "accepted":
            return "friends"

        elif friendship.status == "blocked":
            if friendship.user1 == current_user:
                return "you-blocked"
            else:
                return "blocked-by-user"

        elif friendship.status == "rejected":
            return "request-rejected"

        return friendship.status
    
    def get_friendship_id(self,obj):

        request = self.context.get('request', None)
        if not request or not hasattr(request, 'user'):
            return None

        current_user = request.user

        # Try both directions: user1 -> user2 or user2 -> user1
        friendship = Friendship.objects.filter(
            Q(user1=current_user, user2=obj) | Q(user1=obj, user2=current_user)
        ).first()

        if not friendship:
            return None
        else:
            return friendship.id


class LeaderboardUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    first_name = serializers.CharField()
    profile_photo = serializers.ImageField()
    subscription_type = serializers.CharField()
    total_points = serializers.IntegerField()
    level = serializers.IntegerField()
    index = serializers.IntegerField()


class UserBadgeSerializer(serializers.Serializer):
    badge_id = serializers.IntegerField(source="badge.id")
    badge_name = serializers.CharField(source="badge.name")
    is_completed = serializers.BooleanField()